package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_153 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function HangRoll_153()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 11, this.frame12, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame12():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_run_start");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

