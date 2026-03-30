package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class NeutralAir_51 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function NeutralAir_51()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6, 10, this.frame11, 14, this.frame15, 20, this.frame21, 21, this.frame22, 27, this.frame28);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
            this.self.fireProjectile("chibi_nairProj");
        }

        internal function frame6():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            this.self.updateAttackBoxStats(1, {
                "effectSound":"brawl_kick_l",
                "direction":45,
                "damage":10,
                "power":10,
                "kbConstant":98
            });
            this.self.updateAttackBoxStats(2, {
                "effectSound":"brawl_kick_l",
                "direction":45,
                "damage":10,
                "power":10,
                "kbConstant":98
            });
            this.self.refreshAttackID();
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }


    }
}

