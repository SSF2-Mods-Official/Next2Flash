package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class NAir_114 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var playsound:Number;
        public var audio:Number;

        public function NAir_114()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 7, this.frame8, 9, this.frame10, 11, this.frame12, 13, this.frame14, 18, this.frame19, 20, this.frame21, 23, this.frame24, 24, this.frame25, 29, this.frame30);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame4():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_kirby_nair", {
                "scaleX":1.3,
                "scaleY":1.3,
                "x":0,
                "y":2,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
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

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "hitStun":3,
                "selfHitStun":1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":8,
                "hitStun":3,
                "selfHitStun":1
            });
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame10():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "hitStun":2,
                "selfHitStun":1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "hitStun":2,
                "selfHitStun":1
            });
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame14():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame19():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame25():*
        {
            this.self.removeAllEffects();
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

