package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class FAir_121 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function FAir_121()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 7, this.frame8, 16, this.frame17, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(23),
                "y":-20
            });
        }

        internal function frame5():*
        {
            this.self.addEffectToList(this.self.attachEffect("cfalcon_fairsparkle", {
                "x":this.self.flipX(33),
                "y":-20,
                "parentLock":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame7():*
        {
            this.self.attachEffect("wind_wave", {
                "x":this.self.flipX(28),
                "y":-20,
                "scaleX":0.6,
                "scaleY":0.6,
                "parentLock":true
            });
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
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "direction":42,
                "power":35,
                "kbConstant":80,
                "shock":false,
                "hitStun":2,
                "selfHitStun":1,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_kick_s"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "direction":42,
                "power":35,
                "kbConstant":80,
                "shock":false,
                "hitStun":2,
                "selfHitStun":1,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_kick_s"
            });
        }

        internal function frame17():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("falcon_dspecLand");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

