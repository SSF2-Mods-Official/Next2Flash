package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class BAir_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function BAir_58()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 9, this.frame10, 10, this.frame11, 24, this.frame25, 25, this.frame26, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame5():*
        {
            this.self.setLandingLag(true);
            this.self.playSound("gw_aerial1");
        }

        internal function frame6():*
        {
            this.self.playSound("gw_aerial2");
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame8():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "direction":30,
                "power":60,
                "kbConstant":85
            });
        }

        internal function frame10():*
        {
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "direction":50,
                "damage":3,
                "power":40,
                "kbConstant":60
            });
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

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}

