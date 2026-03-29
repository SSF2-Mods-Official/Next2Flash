package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class USpecial_105 extends MovieClip
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

        public function USpecial_105()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 16, this.frame17, 17, this.frame18, 21, this.frame22, 22, this.frame23, 27, this.frame28, 33, this.frame34, 40, this.frame41, 41, this.frame42, 44, this.frame45, 45, this.frame46, 49, this.frame50, 60, this.frame61, 68, this.frame69);
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
            this.self.attachEffect("uspecSparkle");
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
                this.self.addEventListener(SSF2Event.CHAR_ATTACK_COMPLETE, this.self.toHelpless);
            };
        }

        internal function frame5():*
        {
            this.self.createTimer(1, 0, this.alterHoriz);
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(18),
                "y":-5
            });
        }

        internal function frame9():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame10():*
        {
            this.self.setXSpeed(this.horiz, false);
            this.self.setYSpeed(-23);
            this.self.createTimer(1, 14, this.checkGrabbed);
            this.self.createTimer(1, 3, this.afterImage);
            this.self.destroyTimer(this.alterHoriz);
        }

        internal function frame11():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":2
            });
        }

        internal function frame12():*
        {
            this.self.createTimer(2, 3, this.afterImage);
            this.self.updateAttackStats({"xSpeedCap":7});
        }

        internal function frame17():*
        {
            this.self.createTimer(3, 2, this.afterImage);
        }

        internal function frame18():*
        {
            if (this.self.isOnGround())
            {
                this.self.toHeavyLand();
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame22():*
        {
            this.self.playSound("raptorBoost1");
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame23():*
        {
            this.self.updateAttackStats({"xSpeedDecayAir":-1.65});
        }

        internal function frame28():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame34():*
        {
        }

        internal function frame41():*
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

        internal function frame42():*
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

        internal function frame45():*
        {
            this.self.resetMovement();
        }

        internal function frame46():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_firehit_heavy"});
            this.self.refreshAttackID();
            this.self.resetMovement();
        }

        internal function frame50():*
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
                "y":-30
            });
            this.self.playVoiceSound(1);
            this.self.updateAttackStats({"air_ease":-1});
            SSF2API.getCamera().shake(5);
        }

        internal function frame61():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }


    }
}

