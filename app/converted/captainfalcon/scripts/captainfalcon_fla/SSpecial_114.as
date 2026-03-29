package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecial_114 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var hasHit:*;
        public var grounded:Boolean;
        public var effect1:*;

        public function SSpecial_114()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 7, this.frame8, 17, this.frame18, 19, this.frame20, 30, this.frame31, 32, this.frame33, 33, this.frame34, 35, this.frame36, 38, this.frame39, 47, this.frame48, 48, this.frame49, 52, this.frame53, 62, this.frame63);
        }

        public function toFrame(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toFrame);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT_SHIELD, this.toFrame);
            this.self.destroyTimer(this.checkGround);
            this.self.stancePlayFrame("afterHit");
        }

        public function followCF(_arg_1:*=null):void
        {
            if (this.currentFrame >= 15)
            {
                this.self.destroyTimer(this.followCF);
            };
        }

        public function checkGround():*
        {
            this.grounded = this.self.isOnGround();
            if (!this.grounded)
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.4));
                this.self.stancePlayFrame("fall");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.hasHit = false;
            if (SSF2API.isReady())
            {
                this.grounded = this.self.isOnGround();
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toFrame);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT_SHIELD, this.toFrame);
                this.self.addEffectToList(this.self.attachEffect("raptorboost_effect", {
                    "syncHitStun":true,
                    "parentLock":true
                }));
            };
        }

        internal function frame2():*
        {
            this.self.playSound("raptorBoost1");
            this.self.clearEffectsOnStateChange();
        }

        internal function frame7():*
        {
            this.effect1 = this.self.attachEffect("raptorboost_effect_trail", {"parentLock":true});
            this.self.addEffectToList(this.effect1);
            this.self.createTimer(1, 0, this.followCF);
        }

        internal function frame8():*
        {
            this.self.setXSpeed(21.6, false);
            this.self.createTimer(2, 7, this.checkGround);
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame18():*
        {
            this.self.resetMovement();
            this.self.setXSpeed(0);
            this.self.updateAttackStats({"canFallOff":false});
            this.self.attachEffect("global_dust_cloud");
            this.effect1.gotoAndStop("end");
        }

        internal function frame20():*
        {
            SSF2API.getCamera().shake(4);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("falcon_dspecLand");
            };
        }

        internal function frame31():*
        {
            this.self.resetMovement();
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }

        internal function frame34():*
        {
            this.hasHit = true;
            this.self.updateAttackBoxStats(1, {
                "allowTurboInterrupt":true,
                "damage":7,
                "direction":90,
                "power":78,
                "kbConstant":65,
                "hitStun":1,
                "hitLag":-1.1,
                "selfHitStun":0,
                "hasEffect":true,
                "effect_id":"effect_firehit_light",
                "effectSound":"brawl_punch_m",
                "bypassShield":false,
                "priority":4
            });
            this.self.updateAttackStats({"canFallOff":false});
            this.effect1.gotoAndStop("end");
            this.self.addEffectToList(this.self.attachEffect("raptorboost_ground_hit", {
                "syncHitStun":true,
                "parentLock":true
            }));
        }

        internal function frame36():*
        {
            this.self.resetMovement();
            this.self.setXSpeed(0);
            this.checkGround();
        }

        internal function frame39():*
        {
            this.self.playSound("cfalcon_swing_l");
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }

        internal function frame49():*
        {
            this.self.destroyTimer(this.checkGround);
            this.effect1.gotoAndStop("end");
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame53():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame63():*
        {
            this.self.endAttack();
        }


    }
}

