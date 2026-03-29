package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_56 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function UAir_56()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 10, this.frame11, 17, this.frame18, 18, this.frame19, 19, this.frame20, 24, this.frame25);
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
            this.self.playSound("beep_high");
            this.self.setLandingLag(true);
        }

        internal function frame11():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "damage":9,
                "direction":90,
                "power":70,
                "kbConstant":80
            });
            this.self.playSound("beep_high");
        }

        internal function frame18():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
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

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

