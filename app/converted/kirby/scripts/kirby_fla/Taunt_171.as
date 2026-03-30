package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunt_171 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Taunt_171()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 24, this.frame25, 30, this.frame31, 39, this.frame40, 45, this.frame46, 51, this.frame52, 57, this.frame58, 64, this.frame65, 76, this.frame77, 78, this.frame79, 81, this.frame82, 89, this.frame90, 95, this.frame96, 101, this.frame102, 113, this.frame114, 117, this.frame118, 127, this.frame128);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", true);
            };
        }

        internal function frame9():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_kirby_taunt01", true);
            };
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame25():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_crouch_start");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }

        internal function frame40():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_cmn_spin2");
        }

        internal function frame46():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_cmn_spin2");
        }

        internal function frame52():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_cmn_spin2");
        }

        internal function frame58():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_cmn_spin2");
        }

        internal function frame65():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_kirby_taunt03", true);
            };
            this.self.playSound("ssf2_snd_sfx_kirby_run_stop");
        }

        internal function frame77():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_crouch_start");
            };
        }

        internal function frame79():*
        {
            this.self.endAttack();
        }

        internal function frame82():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame90():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_crouch_start");
            };
        }

        internal function frame96():*
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

        internal function frame102():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame114():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_crouch_start");
            };
        }

        internal function frame118():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
            this.self.playSound("ssf2_snd_sfx_kirby_taunt02");
            this.self.attachEffect("effect_kirby_land", {
                "scaleX":2,
                "scaleY":2,
                "behind":true
            });
        }

        internal function frame128():*
        {
            this.self.endAttack();
        }


    }
}

