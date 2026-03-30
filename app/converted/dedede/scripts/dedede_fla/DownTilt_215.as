package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DownTilt_215 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;

        public function DownTilt_215()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 7, this.frame8, 10, this.frame11, 12, this.frame13, 14, this.frame15, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.attachEffect("global_dust_heavy", {
                    "x":this.self.flipX(-4),
                    "y":3,
                    "scaleX":-0.5,
                    "scaleY":-0.5
                });
            };
        }

        internal function frame2():*
        {
            this.self.setXSpeed(13, false);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame3():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.playSound("ssf2_snd_sfx_dedede_swing_l");
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "hitStun":3,
                "selfHitStun":1,
                "effect_id":"effect_hit3",
                "direction":45,
                "power":60,
                "kbConstant":75,
                "effectSound":"brawl_kick_m"
            });
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame13():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame15():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame19():*
        {
            if (this.self.getControls().DOWN)
            {
                this.self.setGlobalVariable("usedDtilt", false);
            }
            else
            {
                this.self.setGlobalVariable("usedDtilt", true);
            };
            this.self.endAttack();
        }


    }
}

