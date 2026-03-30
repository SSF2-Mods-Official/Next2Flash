package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dair_47 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var ySpeed:*;
        public var xSpeed:*;
        public var dir:*;
        public var bkb:*;

        public function bomberman_dair_47()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 12, this.frame13, 15, this.frame16, 16, this.frame17, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame5():*
        {
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_blast", {
                "y":2,
                "parentLock":true
            });
            this.ySpeed = this.self.getYSpeed();
            this.xSpeed = this.self.getXSpeed();
            this.dir = (Math.atan2(this.ySpeed, this.xSpeed) * (-180 / Math.PI));
            this.bkb = (Math.sqrt(((this.ySpeed * this.ySpeed) + (this.xSpeed * this.xSpeed))) * 4);
            if (!this.self.isFacingRight())
            {
                this.dir = (180 - this.dir);
            };
            if (this.dir < 0)
            {
                this.dir += 360;
            };
            this.self.updateAttackBoxStats(1, {
                "direction":this.dir,
                "power":this.bkb
            });
            this.self.updateAttackBoxStats(2, {
                "direction":this.dir,
                "power":this.bkb
            });
            SSF2API.print(((this.xSpeed.toString() + " | ") + this.ySpeed.toString()));
            SSF2API.print(((this.dir.toString() + " | ") + this.bkb.toString()));
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "direction":90,
                "power":90,
                "kbConstant":58
            });
            this.self.updateAttackBoxStats(2, {
                "direction":90,
                "power":90,
                "kbConstant":58
            });
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(5),
                "y":12,
                "parentLock":true
            });
        }

        internal function frame13():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

