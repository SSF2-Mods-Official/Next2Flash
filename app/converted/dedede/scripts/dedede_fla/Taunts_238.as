package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunts_238 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var hitBox7:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var soundLoop:*;

        public function Taunts_238()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 15, this.frame16, 24, this.frame25, 34, this.frame35, 40, this.frame41, 75, this.frame76, 82, this.frame83, 94, this.frame95, 102, this.frame103, 108, this.frame109, 115, this.frame116, 122, this.frame123, 136, this.frame137, 140, this.frame141);
        }

        public function delayRapidJabSound():*
        {
            this.loopRapidJabSound();
            this.self.createTimer(8, -1, this.loopRapidJabSound);
        }

        public function loopRapidJabSound(_arg_1:*=null):*
        {
            SSF2API.stopSound(this.soundLoop);
            if (!this.soundLoop)
            {
                this.soundLoop = this.self.playSound("ssf2_snd_sfx_dedede_rapidJab");
            }
            else
            {
                this.soundLoop = this.self.playSound("ssf2_snd_sfx_dedede_rapidJab_loop");
            };
        }

        public function stopRapidJabSound(_arg_1:*=null):*
        {
            this.self.destroyTimer(this.delayRapidJabSound);
            this.self.destroyTimer(this.loopRapidJabSound);
            SSF2API.stopSound(this.soundLoop);
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.stopRapidJabSound);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame9():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
        }

        internal function frame16():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
        }

        internal function frame25():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt01", true);
            };
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.stopRapidJabSound);
            this.loopRapidJabSound();
            this.self.createTimer(15, 1, this.delayRapidJabSound);
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt02", true);
            };
        }

        internal function frame76():*
        {
            this.stopRapidJabSound();
        }

        internal function frame83():*
        {
            this.self.endAttack();
        }

        internal function frame95():*
        {
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt03_01", true);
            };
        }

        internal function frame103():*
        {
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt03_02", true);
            };
        }

        internal function frame109():*
        {
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt03_03", true);
            };
        }

        internal function frame116():*
        {
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt03_04", true);
            };
        }

        internal function frame123():*
        {
            SSF2API.getCamera().shake(1);
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_taunt03_05", true);
            };
        }

        internal function frame137():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame141():*
        {
            this.self.endAttack();
        }


    }
}

