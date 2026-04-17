package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class Fox_dthrow_72 extends MovieClip
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
        public var chance:*;

        public function Fox_dthrow_72()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.projectile = null;
            this.chance = 0;
        }

        internal function frame2():*
        {
            this.self.forceGrabbedHurtFrame("faint");
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.playAttackSound(2);
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame9():*
        {
            this.self.fireProjectile("dthrowLaser");
            this.self.playAttackSound(1);
        }

        internal function frame10():*
        {
            this.projectile = this.self.getCurrentProjectile();
            if (this.projectile != null)
            {
                this.projectile.setXSpeed(-4);
            };
            this.self.playAttackSound(1);
            this.self.attachEffect("fox_blasterEffectDown");
        }

        internal function frame11():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.self.fireProjectile("dthrowLaser");
            this.self.playAttackSound(1);
            this.self.forceGrabbedHurtFrame("downed");
            this.self.attachEffect("fox_blasterEffectDown");
        }

        internal function frame13():*
        {
            this.projectile = this.self.getCurrentProjectile();
            if (this.projectile != null)
            {
                this.projectile.setXSpeed(-4);
            };
            this.self.playAttackSound(1);
            SSF2API.getCamera().shake(9);
        }

        internal function frame27():*
        {
            this.chance = SSF2API.random();
            if ((this.chance <= 0.05) && (this.self.getCPULevel() >= 8) && this.self.isCPU())
            {
                this.self.importCPUControls([0, 1, 512, 3, 256, 2, 0, 1, 32, 1]);
            };
            if ((this.chance > 0.05) && (this.chance <= 0.8) && this.self.isCPU())
            {
                this.self.importCPUControls([0, 1, 1088, 1]);
            };
            this.self.endAttack();
        }


    }
}

