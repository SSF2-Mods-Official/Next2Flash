package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_34 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Run_34()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 12, this.frame13, 16, this.frame17, 17, this.frame18, 19, this.frame20, 25, this.frame26, 26, this.frame27, 27, this.frame28, 34, this.frame35, 37, this.frame38);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame5():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame17():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame18():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_runstart");
        }

        internal function frame20():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame26():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
            SSF2API.getCamera().shake(1);
        }

        internal function frame27():*
        {
            this.self.stancePlayFrame("runMid");
        }

        internal function frame28():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_runstart");
        }

        internal function frame35():*
        {
            this.self.playSound("dedede_step1");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
            SSF2API.getCamera().shake(1);
        }

        internal function frame38():*
        {
            this.self.stancePlayFrame("runMid");
        }


    }
}

