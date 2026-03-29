package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpAttack_108 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Get_UpAttack_108()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 15, this.frame16, 17, this.frame18, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.playSound("beep_jump");
            };
        }

        internal function frame7():*
        {
            this.self.playSound("gw_ftilt01");
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame16():*
        {
            this.self.refreshAttackID();
            this.self.playSound("gw_ftilt01");
        }

        internal function frame18():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

