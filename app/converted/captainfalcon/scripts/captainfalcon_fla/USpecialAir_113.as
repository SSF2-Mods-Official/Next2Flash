package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class USpecialAir_113 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:CaptainExt;
        public var horiz:*;
        public var continuePlaying:Boolean;
        public var foe:*;

        public function USpecialAir_113()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 14, this.frame15, 15, this.frame16, 19, this.frame20, 22, this.frame23, 31, this.frame32, 39, this.frame40, 40, this.frame41, 43, this.frame44, 44, this.frame45, 48, this.frame49, 59, this.frame60, 67, this.frame68);
        }

        public function alterHoriz():void
        {
            var _local_1:* = this.self.getControls();
            if ((this.self.isFacingRight() && _local_1.RIGHT) || (!(this.self.isFacingRight()) && _local_1.LEFT))
            {
                this.horiz = 8;
            }
            else if ((this.self.isFacingRight() && _local_1.LEFT) || (!(this.self.isFacingRight()) && _local_1.RIGHT))
            {
                this.horiz = 6;
            }
            else
            {
                this.horiz = 7;
            };
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function checkGrabbed():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.gotoGrabbedCharacter();
                this.self.stancePlayFrame("grabbed");
                this.self.playSound("commandGrab_2");
                this.self.addEffectToList(this.self.attachEffect("cmd_grabbed_gfx", {
                    "x":this.self.flipX(20),
                    "y":-28,
                    "scaleX":-0.4,
                    "scaleY":-0.4
                }));
                this.self.clearEffectsOnStateChange();
            };
        }

        public function afterImage():void
        {
            this.self.attachEffect("uspecSparkle", {"y":10});
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.horiz = 7;
            if (SSF2API.isReady() && this.self)
            {
                this.continuePlaying = false;
                this.self.playAttackSound(1);
                this.self.setXSpeed((this.self.getXSpeed() * 0.5));
                this.self.setYSpeed((this.self.getYSpeed() * 0.5));
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, 0, this.alterHoriz);
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(18),
                "y":5
            });
        }

        internal function frame6():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame7():*
        {
            this.self.setXSpeed(this.horiz, false);
            this.self.setYSpeed(-23);
            this.self.createTimer(1, 14, this.checkGrabbed);
            this.self.createTimer(1, 3, this.afterImage);
            this.self.destroyTimer(this.alterHoriz);
        }

        internal function frame8():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":2
            });
        }

        internal function frame9():*
        {
            this.self.createTimer(2, 3, this.afterImage);
        }

        internal function frame15():*
        {
            this.self.createTimer(3, 2, this.afterImage);
            this.self.updateAttackStats({"xSpeedCap":7});
        }

        internal function frame16():*
        {
            if (this.self.isOnGround())
            {
                this.self.toHeavyLand();
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame20():*
        {
            this.self.playSound("raptorBoost1");
        }

        internal function frame23():*
        {
            this.self.updateAttackStats({
                "xSpeedDecayAir":-1.65,
                "air_ease":-1
            });
        }

        internal function frame32():*
        {
        }

        internal function frame40():*
        {
            if (this.self.isOnGround())
            {
                this.self.toLand();
            }
            else
            {
                this.self.setGlobalVariable("usedSpec", true);
                this.self.toHelpless();
            };
        }

        internal function frame41():*
        {
            this.self.resetMovement();
            this.self.updateAttackStats({
                "allowControl":false,
                "air_ease":0
            });
            this.self.unnattachFromGround();
            this.self.removeEventListener(SSF2Event.CHAR_ATTACK_COMPLETE, this.self.toHelpless);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.self.destroyTimer(this.checkGrabbed);
            this.self.destroyTimer(this.afterImage);
        }

        internal function frame44():*
        {
            this.self.resetMovement();
        }

        internal function frame45():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_firehit_heavy"});
            this.self.refreshAttackID();
            this.self.resetMovement();
        }

        internal function frame49():*
        {
            this.self.setXSpeed(-6, false);
            this.self.setYSpeed(-20);
            this.self.playAttackSound(2);
            this.foe = this.self.getGrabbedOpponent();
            this.self.releaseOpponent();
            if (this.foe)
            {
                this.foe.forceHitStun(1, 0);
            };
            this.self.attachEffect("effect_explosion", {
                "scaleX":1.5,
                "scaleY":1.5,
                "x":this.self.flipX(20),
                "y":-25
            });
            this.self.playVoiceSound(1);
            this.self.updateAttackStats({"air_ease":-1});
            SSF2API.getCamera().shake(5);
        }

        internal function frame60():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }


    }
}

