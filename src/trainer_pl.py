import math
from utils import auto_init_args
from typing import Tuple, Type
import pytorch_lightning as pl
import torch.nn.functional as F
from models import Discriminator, Generator
import torch
from processing import translate_and_project, random_rotate, scale_3d


class VAEGAN(pl.LightningModule):
    def __init__(
        self,
        opt,
        **kwargs,
    ) -> None:
        super().__init__()
        auto_init_args(self)
        self.opt = opt
        self.generator = Generator(opt.latent_dim)
        self.discriminator = Discriminator()
        self.automatic_optimization = False
        self.project_dist = 10
        self.w_recon = opt.lambda_recon
        self.w_g = opt.lambda_g
        self.w_kld = opt.lambda_kld

    def forward(self, x):
        return self.generator(x)

    def training_step(self, batch, batch_idx):
        """TODO add miss joint augmentation, noise for disc. training"""
        if not self.opt.is_ss:
            return self.supervised_step(batch)

        inp, target = batch["pose2d"].detach(), batch["pose2d"].detach()
        recon_3d, mean, logvar = self.generator(inp)
        recon_2d = translate_and_project(recon_3d, self.project_dist)
        loss_recon = self.recon_loss(recon_2d, target, batch["mask"])
        loss_kld = self.kld_loss(mean, logvar)

        # fakes to train G and D
        novel_2d = translate_and_project(random_rotate(recon_3d), self.project_dist)
        reals, fakes = self.get_label(inp)
        opt_g, opt_d = self.optimizers()
        """Train D"""
        opt_d.zero_grad(set_to_none=True)
        # with real
        out = self.discriminator(inp)
        loss_d_real = self.adversarial_loss(out, reals)
        self.manual_backward(loss_d_real)
        D_x = out.mean().item()
        # with fake
        out = self.discriminator(novel_2d.detach())
        loss_d_fake = self.adversarial_loss(out, fakes)
        self.manual_backward(loss_d_fake)
        D_G_z1 = out.mean().item()
        loss_d = loss_d_real + loss_d_fake
        opt_d.step()

        """Train G"""
        opt_g.zero_grad(set_to_none=True)
        # with same fake/ novel_2d sample
        out = self.discriminator(novel_2d)
        loss_g = self.adversarial_loss(out, reals, top_k=True)  # includes Enc.
        loss_vae = self.w_g * loss_g + self.w_recon * loss_recon + self.w_kld * loss_kld
        # G -> realistic + proj recon acc. | Would be diff. if only decoder is G.
        self.manual_backward(loss_vae)
        D_G_z2 = out.mean().item()
        opt_g.step()


    def validation_step(self, batch, batch_idx):
        if not self.opt.is_ss:
            return self.supervised_step(batch)

        inp, target = batch["pose2d"].detach(), batch["pose2d"].detach()
        recon_3d, mean, logvar = self.generator(inp)
        recon_2d = translate_and_project(recon_3d, self.project_dist)
        loss_recon = self.recon_loss(recon_2d, target, batch["mask"])
        loss_kld = self.kld_loss(mean, logvar)

        # fakes to train G and D
        novel_2d = translate_and_project(random_rotate(recon_3d), self.project_dist)
        reals, fakes = self.get_label(inp)
        """Train D"""
        opt_d.zero_grad(set_to_none=True)
        # with real
        out = self.discriminator(inp)
        loss_d_real = self.adversarial_loss(out, reals)
        self.manual_backward(loss_d_real)
        D_x = out.mean().item()
        # with fake
        out = self.discriminator(novel_2d.detach())
        loss_d_fake = self.adversarial_loss(out, fakes)
        self.manual_backward(loss_d_fake)
        D_G_z1 = out.mean().item()
        loss_d = loss_d_real + loss_d_fake
        opt_d.step()

        """Train G"""
        opt_g.zero_grad(set_to_none=True)
        # with same fake/ novel_2d sample
        out = self.discriminator(novel_2d)
        loss_g = self.adversarial_loss(out, reals, top_k=True)  # includes Enc.
        loss_vae = self.w_g * loss_g + self.w_recon * loss_recon + self.w_kld * loss_kld
        # G -> realistic + proj recon acc. | Would be diff. if only decoder is G.
        self.manual_backward(loss_vae)
        D_G_z2 = out.mean().item()
        opt_g.step()

    def supervised_step(self, batch):
        inp, target = batch["pose2d"], batch["pose3d"]
        recon_3d, mean, logvar = self.generator(inp)
        loss = self.recon_loss(recon_3d, target) + self.kld_loss(mean, logvar)  # lambd?
        return loss

    def configure_optimizers(self):
        opt_g = torch.optim.Adam(
            self.generator.parameters(), lr=self.opt.lr_g, betas=(0.5, 0.999)
        )
        opt_d = optimizer = torch.optim.Adam(
            self.discriminator.parameters(), lr=self.opt.lr_d, betas=(0.5, 0.999)
        )  # using SGD worsens Dx

        return [opt_g, opt_d], []  # TODO scheduler

    def top_k_grad(self, loss):
        k = math.ceil(
            max(self.opt.top_k_min, self.opt.top_k_gamma ** self.current_epoch)
            * len(loss)
        )
        loss, top_k_indices = loss.topk(k=k, largest=False, dim=0)
        return loss

    def get_label(self, inp: torch.Tensor, smooth: bool = True):
        """label smoothing for real labels
        TODO flip labels - confuse D.
        """
        real = 1
        fake = 0
        reals = torch.full((len(inp), 1), real).to(inp.device).type_as(inp)
        fakes = reals.fill_(fake)
        if smooth:
            noise = (torch.rand_like(reals) * (0.7 - 1.2)) + 1.2
            reals = reals * noise.to(reals.device).type_as(reals)
        return reals, fakes

    def adversarial_loss(self, y_hat, y, reduction: str = "mean", top_k: bool = False):
        if top_k:
            loss = F.binary_cross_entropy(y_hat, y, reduction="none")
            loss = torch.mean(self.top_k_grad(loss))
            if reduction == "mean":
                return torch.mean(loss)
            if reduction == "sum":
                return torch.sum(loss)

        return F.binary_cross_entropy(y_hat, y, reduction=reduction)

    @staticmethod
    def recon_loss(y_hat, y, occlusion_mask=None):
        if (occlusion_mask != None) and (0 in occlusion_mask):
            y_hat *= occlusion_mask  # 0 if occluded, occlusion is 0 in y
        return F.l1_loss(y_hat, y)

    @staticmethod
    def kld_loss(mean, logvar):
        # mean as recon is mean or reduction is sum for both TODO i guess
        return torch.mean(
            -0.5 * torch.sum(1 + logvar - mean ** 2 - logvar.exp(), dim=1), dim=0
        )
