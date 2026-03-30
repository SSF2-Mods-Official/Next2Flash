package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_33 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var normalwalk:*;

        public function Walk_33()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 16, this.frame17, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.normalwalk = true;
        }

        internal function frame7():*
        {
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
        }

        internal function frame17():*
        {
            SSF2API.getCamera().shake(1);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
        }

        internal function frame20():*
        {
            gotoAndStop("startwalk");
        }


    }
}

