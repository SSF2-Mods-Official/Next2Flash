package kirby_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class JigglypuffKirby_248 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:*;
        public var charge:*;
        public var controls:Object;
        public var dir:*;
        public var ground:*;
        public var trail:*;
        public var xConstantTurn:*;
        public var xconstant:*;
        public var bounce:*;
        public var frameCount:*;
        public var frameInc:*;
        public var turnDelay:*;
        public var turnDelayCount:*;
        public var controlCheckCount:*;
        public var tehLoopCount:Number;

        public function JigglypuffKirby_248()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 9, this.frame10, 15, this.frame16, 19, this.frame20, 21, this.frame22, 27, this.frame28, 32, this.frame33, 33, this.frame34, 36, this.frame37, 38, this.frame39, 39, this.frame40, 41, this.frame42, 42, this.frame43, 50, this.frame51, 58, this.frame59, 59, this.frame60, 67, this.frame68, 75, this.frame76, 76, this.frame77, 80, this.frame81, 84, this.frame85, 88, this.frame89, 92, this.frame93, 93, this.frame94, 97, this.frame98, 101, this.frame102, 102, this.frame103, 103, this.frame104, 109, this.frame110, 110, this.frame111, 129, this.frame130, 130, this.frame131, 139, this.frame140);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function playDust():void
        {
            if ((this.charge == "mid") || (this.charge == "slow"))
            {
                this.self.attachEffect("global_dust_light");
            }
            else
            {
                this.self.attachEffect("global_dust_heavy");
            };
        }

        public function chargeIt():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                gotoAndStop("slowGo");
            };
        }

        public function turnCheck():void
        {
            this.controls = this.self.getControls();
            if ((this.self.isOnGround() && this.dir && this.controls.LEFT) || (this.self.isOnGround() && !(this.dir) && this.controls.RIGHT))
            {
                this.self.destroyTimer(this.roll);
                this.self.createTimer(1, -1, this.turn);
                this.self.refreshAttackID();
                this.self.updateAttackStats({"canFallOff":false});
                gotoAndStop("turning");
            };
        }

        public function tick():void
        {
            this.frameCount--;
            if (this.frameCount == 0)
            {
                this.self.destroyTimer(this.turn);
                this.self.destroyTimer(this.roll);
                this.jumpToEnd();
            };
        }

        public function roll():void
        {
            this.self.setXSpeed(this.xconstant, false);
            if (this.trail)
            {
                this.self.attachEffect("global_sparkle", {
                    "x":this.flipX(-10),
                    "y":-15
                });
            };
            if (this.dir)
            {
                this.self.faceRight();
            }
            else
            {
                this.self.faceLeft();
            };
            if (this.turnDelay <= 0)
            {
                this.turnCheck();
            }
            else
            {
                this.turnDelay--;
            };
            this.tick();
        }

        public function turn():void
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.8));
            if (Math.abs(this.self.getXSpeed()) < 1)
            {
                this.self.updateAttackStats({"canFallOff":true});
                if (this.self.isFacingRight())
                {
                    this.self.faceLeft();
                }
                else
                {
                    this.self.faceRight();
                };
                this.dir = (!(this.dir));
                this.self.attachEffect("global_dust_heavy");
                this.self.destroyTimer(this.turn);
                this.self.createTimer(1, -1, this.roll);
                this.turnDelayCount = this.turnDelay;
                gotoAndStop((this.charge + "Go"));
            };
            this.tick();
        }

        public function startRoll():void
        {
            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToAfterHit);
            this.self.addEventListener(SSF2Event.HIT_WALL, this.jumpToAfterHit);
            this.self.destroyTimer(this.controlCheck);
            this.self.destroyTimer(this.playDust);
            this.self.createTimer(1, -1, this.roll);
            this.gotoAndStop((this.charge + "Go"));
        }

        public function controlCheck():void
        {
            this.controlCheckCount++;
            this.controls = this.self.getControls();
            if (!(this.controls.BUTTON1) && (this.controlCheckCount > 5))
            {
                this.startRoll();
            };
        }

        public function jumpToEnd():*
        {
            this.self.addEventListener(SSF2Event.HIT_WALL, this.jumpToAfterHit);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToAfterHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
            this.self.destroyTimer(this.jumpToEnd);
            this.gotoAndStop("end");
        }

        public function jumpToAfterHit(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.jumpToAfterHit);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToAfterHit);
            gotoAndStop("afterHit");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.createTimer(5, -1, this.playDust);
            };
            this.xframe = "charging";
            this.charge = "slow";
            this.controls = null;
            this.dir = null;
            this.ground = null;
            this.trail = false;
            this.xConstantTurn = 0;
            this.xconstant = 0;
            this.bounce = 5;
            this.frameCount = 45;
            this.frameInc = 24;
            this.turnDelay = 7;
            this.turnDelayCount = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.dir = this.self.isFacingRight();
                this.ground = this.self.isOnGround();
            };
            this.controlCheckCount = 0;
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.controlCheck);
        }

        internal function frame8():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            };
        }

        internal function frame10():*
        {
            this.self.playSound("jiggs_rollout2");
        }

        internal function frame16():*
        {
            this.self.playSound("jiggs_rollout2");
        }

        internal function frame20():*
        {
            this.charge = "mid";
            this.self.destroyTimer(this.playDust);
            this.self.createTimer(4, -1, this.playDust);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(15),
                "y":-20
            });
            this.frameCount += this.frameInc;
        }

        internal function frame22():*
        {
            this.self.playSound("jiggs_rollout2");
        }

        internal function frame28():*
        {
            this.self.playSound("jiggs_rollout2");
            this.charge = "midHigh";
            this.self.destroyTimer(this.playDust);
            this.self.createTimer(4, -1, this.playDust);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(10),
                "y":-30
            });
            this.frameCount += this.frameInc;
        }

        internal function frame33():*
        {
            this.self.playVoiceSound(1);
            this.self.destroyTimer(this.playDust);
            this.self.createTimer(3, -1, this.playDust);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(20),
                "y":-18
            });
            this.frameCount += (this.frameInc * 1.5);
        }

        internal function frame34():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-20),
                "y":-20
            });
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(-10),
                "y":-15
            });
            this.self.attachEffect("global_dust_heavy");
            this.charge = "full";
        }

        internal function frame37():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(20),
                "y":-5
            });
        }

        internal function frame39():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame40():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame42():*
        {
            this.gotoAndStop("fullCharge");
        }

        internal function frame43():*
        {
            this.self.playSound("jiggs_rollout1");
            this.xconstant = 3;
            this.bounce = 5;
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "power":50,
                "kbConstant":50
            });
        }

        internal function frame51():*
        {
            this.self.playSound("jiggs_rollout1");
        }

        internal function frame59():*
        {
            gotoAndStop("slowGo");
        }

        internal function frame60():*
        {
            this.self.playSound("jiggs_rollout1");
            this.xconstant = 12;
            this.bounce = 7;
            this.self.updateAttackBoxStats(1, {
                "damage":9,
                "power":70,
                "kbConstant":60
            });
        }

        internal function frame68():*
        {
            this.self.playSound("jiggs_rollout1");
        }

        internal function frame76():*
        {
            gotoAndStop("midGo");
        }

        internal function frame77():*
        {
            this.self.playSound("jiggs_rollout1");
            this.xconstant = 16;
            this.bounce = 9;
            this.self.updateAttackBoxStats(1, {
                "damage":11,
                "power":80,
                "kbConstant":70
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame81():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame85():*
        {
            this.self.playSound("jiggs_rollout1");
            this.self.attachEffect("global_dust_light");
        }

        internal function frame89():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame93():*
        {
            this.gotoAndStop("midHighGo");
        }

        internal function frame94():*
        {
            this.self.playSound("jiggs_rollout1");
            this.xconstant = 20;
            this.bounce = 10;
            this.trail = true;
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "power":100,
                "kbConstant":80
            });
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(-10),
                "y":-15
            });
            this.self.attachEffect("jigglypuff_nspec_wind", {
                "x":this.flipX(-10),
                "y":-15
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame98():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(-10),
                "y":-15
            });
            this.self.attachEffect("jigglypuff_nspec_wind", {
                "x":this.flipX(-10),
                "y":-15
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame102():*
        {
            this.gotoAndStop("fullGo");
        }

        internal function frame103():*
        {
            this.self.updateAttackStats({"xSpeedDecay":0});
            this.self.setXSpeed(0);
            this.self.unnattachFromGround();
            this.self.setXSpeed(-1, false);
            this.self.setYSpeed(-(this.bounce));
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
            this.tehLoopCount = 0;
            this.self.destroyTimer(this.roll);
            this.self.destroyTimer(this.turn);
        }

        internal function frame104():*
        {
            this.tehLoopCount++;
        }

        internal function frame110():*
        {
            this.gotoAndStop("loop");
            if (this.tehLoopCount > 3)
            {
                this.self.updateAttackStats({
                    "allowFullInterrupt":true,
                    "allowDoubleJump":true,
                    "doubleJumpCancelAttack":true
                });
            };
        }

        internal function frame111():*
        {
            this.self.setXSpeed(3, false);
            this.self.updateAttackStats({"xSpeedDecay":-0.1});
            this.self.destroyTimer(this.roll);
        }

        internal function frame130():*
        {
            this.self.endAttack("land");
        }

        internal function frame131():*
        {
            this.self.updateAttackStats({"canFallOff":false});
            this.self.updateAttackBoxStats(1, {"damage":3});
        }

        internal function frame140():*
        {
            gotoAndStop("turning");
        }


    }
}

