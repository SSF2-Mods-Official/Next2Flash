package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DAir_59 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function DAir_59()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 5, this.frame6, 21, this.frame22, 22, this.frame23, 34, this.frame35);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
                if (this.self.getYSpeed() > -4)
                {
                    this.self.setYSpeed(-4);
                };
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.updateAttackStats({"air_ease":-1});
            this.self.setXSpeed(0);
            this.self.setYSpeed(17);
            this.self.playSound("gw_aerial1");
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":7,
                "direction":60,
                "kbConstant":50
            });
            this.self.playSound("gw_aerial2");
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "direction":60,
                "damage":3.5,
                "priority":3,
                "power":60,
                "kbConstant":50,
                "hitLag":-1.1
            });
            SSF2API.getCamera().shake(5);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("beep_dair_landing");
            };
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }


    }
}

