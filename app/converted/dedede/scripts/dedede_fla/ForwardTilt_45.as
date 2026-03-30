package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardTilt_45 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var attackBox4:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;

        public function ForwardTilt_45()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 10, this.frame11, 23, this.frame24);
        }

        public function doSound(_arg_1:int):*
        {
            if (this.audio != _arg_1)
            {
                this.self.playVoiceSound(_arg_1);
                this.self.setGlobalVariable("audio", _arg_1);
            }
            else
            {
                this.self.setGlobalVariable("audio", 0);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame6():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_uair");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            if (this.playsound > 0.8)
            {
                this.doSound(4);
            }
            else if (this.playsound > 0.6)
            {
                this.doSound(3);
            }
            else if (this.playsound > 0.4)
            {
                this.doSound(2);
            }
            else if (this.playsound > 0.2)
            {
                this.doSound(1);
            }
            else
            {
                this.self.setGlobalVariable("audio", 0);
            };
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame8():*
        {
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":3,
                "direction":50,
                "power":30,
                "kbConstant":190,
                "effectSound":"ssf2_snd_sfx_dedede_hit_l",
                "effect_id":"effect_hit1",
                "hitStun":5,
                "selfHitStun":3,
                "camShake":6
            });
            this.self.updateAttackBoxStats(2, {
                "damage":3,
                "direction":50,
                "power":30,
                "kbConstant":190,
                "effectSound":"ssf2_snd_sfx_dedede_hit_l",
                "effect_id":"effect_hit1",
                "hitStun":5,
                "selfHitStun":3,
                "camShake":6
            });
            this.self.refreshAttackID();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

