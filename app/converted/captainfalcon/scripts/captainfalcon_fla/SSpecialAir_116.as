package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecialAir_116 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var hasHit:*;
        public var effect1:*;
        public var self:CaptainExt;

        public function SSpecialAir_116()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 8, this.frame9, 20, this.frame21, 22, this.frame23, 26, this.frame27, 34, this.frame35, 35, this.frame36, 38, this.frame39, 49, this.frame50);
        }

        public function toFrame(_arg_1:*):*
        {
            this.self.stancePlayFrame("afterHit");
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toFrame);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT_SHIELD, this.toFrame);
        }

        public function followCF(_arg_1:*=null):void
        {
            if (this.currentFrame >= 17)
            {
                this.self.destroyTimer(this.followCF);
            };
        }

        internal function frame1():*
        {
            this.hasHit = false;
            this.effect1 = null;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toFrame);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT_SHIELD, this.toFrame);
                this.self.addEventListener(SSF2Event.CHAR_ATTACK_COMPLETE, this.self.toHelpless);
                this.self.attachEffect("raptorboost_effect", {"y":5});
            };
        }

        internal function frame2():*
        {
            this.self.playSound("raptorBoost1");
            this.self.clearEffectsOnStateChange();
        }

        internal function frame8():*
        {
            this.effect1 = this.self.attachEffect("raptorboost_effect_trail", {
                "y":5,
                "parentLock":true
            });
            this.self.createTimer(1, 0, this.followCF);
            this.self.addEffectToList(this.effect1);
        }

        internal function frame9():*
        {
            this.self.setXSpeed(18, false);
            this.self.playAttackSound(2);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame21():*
        {
            this.self.setXSpeed(4, false);
            this.self.updateAttackStats({"xSpeedDecayAir":-0.3});
            this.effect1.gotoAndStop("end");
        }

        internal function frame23():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame27():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame35():*
        {
            if (this.self.isOnGround())
            {
                this.self.endAttack();
            }
            else
            {
                this.self.setGlobalVariable("usedSpec", true);
                this.self.toHelpless();
            };
        }

        internal function frame36():*
        {
            this.hasHit = true;
            this.self.updateAttackStats({"canFallOff":false});
            this.self.updateAttackBoxStats(1, {
                "allowTurboInterrupt":true,
                "damage":7,
                "direction":270,
                "power":40,
                "kbConstant":50,
                "hitStun":4,
                "selfHitStun":4,
                "hasEffect":true,
                "effect_id":"effect_firehit_light",
                "effectSound":"brawl_punch_m",
                "bypassShield":false,
                "priority":4
            });
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.effect1.gotoAndStop("end");
            this.self.addEffectToList(this.self.attachEffect("raptorboost_aerial_hit", {
                "y":5,
                "parentLock":true,
                "syncHitStun":true
            }));
        }

        internal function frame39():*
        {
            this.self.setYSpeed(-7);
            this.self.setXSpeed(8.6, false);
            this.self.updateAttackStats({
                "xSpeedDecayAir":-0.1,
                "air_ease":-1
            });
            this.self.removeEventListener(SSF2Event.CHAR_ATTACK_COMPLETE, this.self.toHelpless);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            this.self.playSound("cfalcon_swing_l");
        }

        internal function frame50():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            this.self.endAttack();
        }


    }
}

