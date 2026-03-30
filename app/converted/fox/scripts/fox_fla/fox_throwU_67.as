package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_throwU_67 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:FoxExt;
        public var projectile:*;
        public var target:*;
        public var grab:*;

        public function fox_throwU_67()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.projectile = null;
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame14():*
        {
            this.self.attachEffect("fox_blasterEffectUp");
        }

        internal function frame15():*
        {
            this.self.fireProjectile("uthrowLaser");
            this.self.playAttackSound(1);
        }

        internal function frame16():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile = this.self.getCurrentProjectile();
                this.projectile.setXSpeed(-1);
            };
            this.self.fireProjectile("uthrowLaser");
            this.self.playAttackSound(1);
            this.self.attachEffect("fox_blasterEffectUp");
        }

        internal function frame17():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile = this.self.getCurrentProjectile();
                this.projectile.setXSpeed(1);
            };
            this.self.fireProjectile("uthrowLaser");
            this.self.playAttackSound(1);
            SSF2API.getCamera().shake(9);
        }

        internal function frame18():*
        {
            this.self.attachEffect("fox_blasterEffectUp");
        }

        internal function frame21():*
        {
            this.target = null;
            this.grab = 0;
            if (this.self.isCPU())
            {
                this.target = this.self.getGrabbedOpponents()[0];
                this.grab = SSF2API.random();
                if ((this.target != null) && (this.target.getDamage() >= 70))
                {
                    if (this.grab <= 0.8)
                    {
                        this.self.importCPUControls([128, 7, 2208, 1]);
                    };
                }
                else if (this.target != null)
                {
                    if ((this.grab <= 0.4) && (this.target.getDamage() <= 50))
                    {
                        this.self.importCPUControls([6305, 1]);
                    }
                    else if (this.grab <= 0.5)
                    {
                        this.self.importCPUControls([128, 7, 4129, 1]);
                    }
                    else if (this.grab <= 0.75)
                    {
                        this.self.importCPUControls([128, 7, 4385, 1]);
                    }
                    else
                    {
                        this.self.importCPUControls([128, 7, 4641, 1]);
                    };
                };
            };
            this.self.endAttack();
        }


    }
}

