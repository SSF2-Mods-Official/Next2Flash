package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_71 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var normalwalk:*;

        public function Walk_71()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 11, this.frame12, 17, this.frame18, 18, this.frame19, 22, this.frame23, 37, this.frame38, 45, this.frame46);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.normalwalk = true;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
            };
        }

        internal function frame5():*
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

        internal function frame12():*
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

        internal function frame18():*
        {
            gotoAndStop("startwalk");
        }

        internal function frame19():*
        {
            this.normalwalk = false;
        }

        internal function frame23():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step01");
            };
        }

        internal function frame38():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step02");
            };
        }

        internal function frame46():*
        {
            gotoAndStop("startwalk2");
        }


    }
}

