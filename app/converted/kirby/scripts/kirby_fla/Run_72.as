package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_72 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Run_72()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 10, this.frame11, 16, this.frame17, 19, this.frame20, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
            };
        }

        internal function frame4():*
        {
            SSF2API.playSound("ssf2_snd_sfx_kirby_run_start");
        }

        internal function frame7():*
        {
            this.gotoAndStop("run");
        }

        internal function frame11():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step01");
            };
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step02");
            };
        }

        internal function frame20():*
        {
            this.gotoAndStop("run");
        }

        internal function frame27():*
        {
            this.gotoAndStop("run");
        }


    }
}

