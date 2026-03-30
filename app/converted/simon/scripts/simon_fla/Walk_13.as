package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_13 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Walk_13()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame8():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_simon_step_01");
            };
        }

        internal function frame21():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_simon_step_02");
            };
        }


    }
}

