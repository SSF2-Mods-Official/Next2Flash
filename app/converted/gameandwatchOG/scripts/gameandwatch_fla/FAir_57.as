package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class FAir_57 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function FAir_57()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 15, this.frame16, 19, this.frame20, 20, this.frame21, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(-18),
                "y":-30
            });
        }

        internal function frame6():*
        {
            this.self.playSound("gw_aerial1");
        }

        internal function frame7():*
        {
            this.self.playSound("gw_aerial2");
        }

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "selfHitStun":2,
                "hitStun":3
            });
        }

        internal function frame16():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }

        internal function frame21():*
        {
            this.self.updateAttackStats({"cancelWhenAirborne":true});
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("snd_se_GW_Landing02");
            };
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }


    }
}

