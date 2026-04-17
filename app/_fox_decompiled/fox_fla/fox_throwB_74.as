package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_throwB_74 extends MovieClip
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
        public var dir:*;

        public function fox_throwB_74()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 9, this.frame10, 12, this.frame13, 15, this.frame16, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.projectile = null;
                this.dir = this.self.isFacingRight();
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame10():*
        {
            this.self.fireProjectile("bthrowLaser");
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile = this.self.getCurrentProjectile();
            };
            this.projectile.setXSpeed(20, false);
            this.self.playAttackSound(1);
            this.self.attachEffect("fox_blasterEffectBack");
        }

        internal function frame13():*
        {
            this.self.fireProjectile("bthrowLaser");
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile = this.self.getCurrentProjectile();
            };
            this.projectile.setXSpeed(22, false);
            this.projectile.setYSpeed(-7);
            this.self.playAttackSound(1);
            this.self.attachEffect("fox_blasterEffectBack");
        }

        internal function frame16():*
        {
            this.self.fireProjectile("bthrowLaser");
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile = this.self.getCurrentProjectile();
            };
            this.projectile.setXSpeed(21, false);
            this.projectile.setYSpeed(-5);
            this.self.playAttackSound(1);
            this.self.attachEffect("fox_blasterEffectBack");
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

