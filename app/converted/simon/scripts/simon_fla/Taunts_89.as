package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunts_89 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Taunts_89()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6, 14, this.frame15, 71, this.frame72, 80, this.frame81, 84, this.frame85, 85, this.frame86, 115, this.frame116, 121, this.frame122, 131, this.frame132, 135, this.frame136, 141, this.frame142, 153, this.frame154, 157, this.frame158);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame3():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_taunt01", true);
            };
        }

        internal function frame6():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_m");
        }

        internal function frame15():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_s");
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

        internal function frame72():*
        {
            this.self.endAttack();
        }

        internal function frame81():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_taunt02", true);
            };
        }

        internal function frame85():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_s");
        }

        internal function frame86():*
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

        internal function frame116():*
        {
            this.self.endAttack();
        }

        internal function frame122():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_m");
        }

        internal function frame132():*
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

        internal function frame136():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_s");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_edgeGrab", true);
            };
        }

        internal function frame142():*
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

        internal function frame154():*
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

        internal function frame158():*
        {
            this.self.endAttack();
        }


    }
}

