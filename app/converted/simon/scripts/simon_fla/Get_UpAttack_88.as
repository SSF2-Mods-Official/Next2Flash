package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpAttack_88 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Get_UpAttack_88()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 11, this.frame12, 15, this.frame16, 20, this.frame21, 23, this.frame24, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame7():*
        {
            this.self.playSound("brawl_swing_s");
        }

        internal function frame12():*
        {
            this.self.playSound("brawl_swing_m");
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame21():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_m1");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_simon_step_01");
                };
            };
        }

        internal function frame24():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_m2");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_simon_step_02");
                };
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

