package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class HangAttack_98 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var bell:*;

        public function HangAttack_98()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 7, this.frame8, 10, this.frame11, 11, this.frame12, 12, this.frame13, 21, this.frame22, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("gw_jump1");
        }

        internal function frame8():*
        {
            this.self.playSound("beep_crouch_2");
        }

        internal function frame11():*
        {
            this.self.setXSpeed(10.5, false);
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_light");
            this.bell = this.self.playSound("snd_se_GW_Special_S01");
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame22():*
        {
            SSF2API.stopSound(this.bell);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

