package fox_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;
    import flash.events.Event;

    public dynamic class fox_landmasterstart_finalform2_142 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:FoxExt;
        public var MIN_THRUST_POWER_FROM_GROUND:*;
        public var MAX_RISE_SPEED:Number;
        public var MAX_FALL_SPEED:Number;
        public var MAX_FALL_SPEED_THRUST:Number;
        public var GRAVITY:Number;
        public var THRUST_GRAVITY:Number;
        public var THRUST_SPEED:Number;
        public var CPU_FIRE_CHECK_RATE:Number;
        public var CPU_TARGET_RATE:Number;
        public var CPU_TARGET_X_DISTANCE_THRESHOLD:Number;
        public var timer:*;
        public var thrustPower:*;
        public var thrusting:Boolean;
        public var firing:Boolean;
        public var finalSmashBar:FinalSmashBar;
        public var cpuControls:ControlBits;
        public var prevCpuControls:ControlBits;
        public var cpuFireTimer:int;
        public var cpuTarget:*;
        public var cpuTargetTimer:int;
        public var cpuPreviousPosition:Point;
        public var cpuStuckPositionFrames:int;
        public var deathBounds:Object;
        public var controls:Object;
        public var finished:Boolean;
        public var character:*;
        public var landmasterFlyingSound:Number;

        public function fox_landmasterstart_finalform2_142()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16, 18, this.frame19, 19, this.frame20, 20, this.frame21, 25, this.frame26, 49, this.frame50, 57, this.frame58, 58, this.frame59, 68, this.frame69, 69, this.frame70, 70, this.frame71, 79, this.frame80, 94, this.frame95, 95, this.frame96, 113, this.frame114, 115, this.frame116, 116, this.frame117, 124, this.frame125, 147, this.frame148, 150, this.frame151, 151, this.frame152, 162, this.frame163, 168, this.frame169, 169, this.frame170);
        }

        public function setupBar():*
        {
            this.finalSmashBar = new FinalSmashBar(this.timer);
            this.finalSmashBar.addToDamageMeter(this.self.getHealthBox());
            this.self.setFinalSmashMeterCharge(0);
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar, {"persistent":true});
        }

        public function clearBar(_arg_1:*=null):*
        {
            this.finalSmashBar.removeFromDamageMeter(this.self.getHealthBox());
            this.finalSmashBar = null;
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar);
        }

        public function removeSelfPlatform(_arg_1:*=null):*
        {
            this.self.removeSelfPlatform();
        }

        public function cleanup(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.cleanup);
            this.self.removeSelfPlatform();
            this.self.updateCharacterStats({"gravity":this.self.getOwnStats().gravity});
        }

        public function finalStartJump():void
        {
            this.self.playAttackSound(1);
        }

        public function finalStartFly():void
        {
            this.self.playAttackSound(2);
        }

        public function foxRise():*
        {
            var _local_1:* = (this.self.getMC().y - 25);
            this.self.getMC().y = _local_1;
            this.self.setY(_local_1);
            if ((this.self.getY() - this.deathBounds.y) <= 100)
            {
                this.self.destroyTimer(this.foxRise);
                this.self.stancePlayFrame("initLandmaster");
            };
        }

        public function avoidWarningBounds():void
        {
            if (this.self.inLowerLeftWarningBounds())
            {
                this.cpuControls.reset();
                this.cpuControls.JUMP = true;
                this.cpuControls.RIGHT = true;
            }
            else
            {
                if (this.self.inLowerRightWarningBounds())
                {
                    this.cpuControls.reset();
                    this.cpuControls.JUMP = true;
                    this.cpuControls.LEFT = true;
                }
                else
                {
                    if (this.self.inUpperLeftWarningBounds())
                    {
                        this.cpuControls.reset();
                        if (!SSF2API.hitTestGroundBetweenPoints(new Point(this.self.getX(), this.self.getY()), new Point(this.self.getX(), (this.self.getY() + 800))))
                        {
                            this.cpuControls.JUMP = true;
                        };
                        this.cpuControls.RIGHT = true;
                    }
                    else
                    {
                        if (this.self.inUpperRightWarningBounds())
                        {
                            this.cpuControls.reset();
                            if (!SSF2API.hitTestGroundBetweenPoints(new Point(this.self.getX(), this.self.getY()), new Point(this.self.getX(), (this.self.getY() + 800))))
                            {
                                this.cpuControls.JUMP = true;
                            };
                            this.cpuControls.LEFT = true;
                        };
                    };
                };
            };
        }

        public function landmasterControlsCPU():*
        {
            var _local_1:Number = NaN;
            var _local_2:Number = NaN;
            var _local_3:Number = NaN;
            if (this.self.isCPU())
            {
                this.cpuTargetTimer++;
                if (this.cpuTargetTimer >= this.CPU_TARGET_RATE)
                {
                    this.cpuTargetTimer = 0;
                    this.cpuTarget = this.self.getNearestPath("character", true)[0] || null;
                };
                this.prevCpuControls.bits = this.cpuControls.bits;
                if ((this.cpuPreviousPosition.x === this.self.getX()) && (this.cpuPreviousPosition.y === this.self.getY()))
                {
                    this.cpuStuckPositionFrames++;
                }
                else
                {
                    this.cpuStuckPositionFrames = 0;
                    this.cpuPreviousPosition.x = this.self.getX();
                    this.cpuPreviousPosition.y = this.self.getY();
                };
                this.cpuControls.reset();
                if (this.cpuTarget != null)
                {
                    _local_1 = (this.cpuTarget.getX() - this.self.getX());
                    _local_2 = (this.cpuTarget.getY() - this.self.getY());
                    _local_3 = ((this.cpuTarget.getType() !== "SSF2Beacon") ? this.CPU_TARGET_X_DISTANCE_THRESHOLD : 5);
                    if (_local_1 > _local_3)
                    {
                        this.cpuControls.RIGHT = true;
                    }
                    else
                    {
                        if (_local_1 < -(_local_3))
                        {
                            this.cpuControls.LEFT = true;
                        };
                    };
                    if ((_local_2 < -(_local_3)) || (this.cpuStuckPositionFrames > 60))
                    {
                        this.cpuStuckPositionFrames = 0;
                        this.cpuControls.JUMP = true;
                    };
                    this.cpuFireTimer++;
                    if (this.self.isOnGround() && !(this.self.isFacingRight()) && (_local_1 > 0))
                    {
                        this.cpuControls.LEFT = false;
                        this.cpuControls.RIGHT = true;
                    }
                    else
                    {
                        if (this.self.isOnGround() && this.self.isFacingRight() && (_local_1 < 0))
                        {
                            this.cpuControls.LEFT = true;
                            this.cpuControls.RIGHT = false;
                        };
                    };
                    if ((this.cpuFireTimer >= this.CPU_FIRE_CHECK_RATE) && !(this.self.inLowerLeftWarningBounds()) && !(this.self.inLowerRightWarningBounds()))
                    {
                        this.cpuFireTimer = 0;
                        if (((_local_1 * _local_2) < (_local_3 * _local_3)) && (this.cpuTarget.getType() !== "SSF2Beacon") && (SSF2API.random() > (1 - (this.self.getCPULevel() / 10))))
                        {
                            if (this.self.isOnGround() && (SSF2API.random() > 0.8) && ((_local_1 * _local_2) < (50 * 50)))
                            {
                                this.cpuControls.DOWN = true;
                            }
                            else
                            {
                                this.cpuControls.BUTTON1 = true;
                            };
                        };
                    };
                };
                this.avoidWarningBounds();
                this.self.importCPUControls([this.cpuControls.bits, 1]);
            };
        }

        public function landmasterControls():*
        {
            var _local_1:Object = this.self.getControls();
            if (this.timer == 0)
            {
                this.self.destroyTimer(this.landmasterControls);
                this.self.destroyTimer(this.startTimer);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.landmasterGrounded);
                this.self.stancePlayFrame("outro");
                return;
            }
            else
            if (this.self.isOnGround())
            {
                if (this.thrustPower < this.MIN_THRUST_POWER_FROM_GROUND)
                {
                    this.thrustPower = this.MIN_THRUST_POWER_FROM_GROUND;
                }
                else
                {
                    this.thrustPower = this.thrustPower;
                };
            };
            if (_local_1.BUTTON1 || _local_1.BUTTON2 || _local_1.GRAB)
            {
                this.self.updateCharacterStats({"gravity":this.GRAVITY});
                this.self.updateAttackStats({"air_ease":this.MAX_FALL_SPEED});
                this.firing = true;
                SSF2API.print("firing");
                this.self.destroyTimer(this.landmasterControls);
                this.self.stancePlayFrame("landmaster_fire");
            }
            else
            {
                if (_local_1.LEFT || _local_1.RIGHT && this.self.isOnGround())
                {
                    if (_local_1.LEFT)
                    {
                        if (this.self.isFacingRight())
                        {
                            this.self.destroyTimer(this.landmasterControls);
                            this.self.stancePlayFrame("turn");
                        }
                        else
                        {
                            this.self.stancePlayFrame("landmaster_walk");
                        };
                    }
                    else
                    {
                        if (_local_1.RIGHT)
                        {
                            if (!this.self.isFacingRight())
                            {
                                this.self.destroyTimer(this.landmasterControls);
                                this.self.stancePlayFrame("turn");
                            }
                            else
                            {
                                this.self.stancePlayFrame("landmaster_walk");
                            };
                        };
                    };
                };
                if (_local_1.JUMP)
                {
                    this.self.updateCharacterStats({"gravity":this.THRUST_GRAVITY});
                    if (this.self.isOnGround())
                    {
                        this.self.stancePlayFrame("landmaster_jump");
                        this.landmasterFlyingSound = this.self.playAttackSound(6);
                        this.self.setYSpeed(this.MAX_RISE_SPEED);
                        this.self.unnattachFromGround();
                    };
                    if (this.thrustPower > 0)
                    {
                        this.self.updateAttackStats({"air_ease":this.MAX_FALL_SPEED_THRUST});
                        this.thrustPower--;
                        this.self.setYSpeed((this.self.getYSpeed() - this.THRUST_SPEED));
                        if (this.self.getYSpeed() < this.MAX_RISE_SPEED)
                        {
                            this.self.setYSpeed(this.MAX_RISE_SPEED);
                        };
                    };
                    if (!this.thrusting)
                    {
                        this.thrusting = true;
                        this.self.stancePlayFrame("landmaster_jump");
                        this.landmasterFlyingSound = this.self.playAttackSound(6);
                    };
                }
                else
                {
                    this.thrusting = false;
                };
                if (_local_1.DOWN && this.self.isOnGround())
                {
                    this.self.destroyTimer(this.landmasterControls);
                    this.self.stancePlayFrame("roll");
                };
            };
        }

        public function startTimer():*
        {
            this.timer--;
            if (this.finalSmashBar != null)
            {
                this.finalSmashBar.updateBar(this.timer);
            };
            if (this.timer == 0)
            {
                this.self.destroyTimer(this.landmasterControls);
                this.self.destroyTimer(this.startTimer);
                this.self.stancePlayFrame("outro");
            };
        }

        public function landmasterGrounded(_arg_1:Event=null):void
        {
            SSF2API.stopSound(this.landmasterFlyingSound);
            this.self.playAttackSound(4);
            if (!this.firing)
            {
                this.self.stancePlayFrame("landmaster_land");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.MIN_THRUST_POWER_FROM_GROUND = (30 * 1);
            this.MAX_RISE_SPEED = -8;
            this.MAX_FALL_SPEED = 15;
            this.MAX_FALL_SPEED_THRUST = 6;
            this.GRAVITY = 2;
            this.THRUST_GRAVITY = 0.5;
            this.THRUST_SPEED = 2;
            this.CPU_FIRE_CHECK_RATE = 15;
            this.CPU_TARGET_RATE = 30;
            this.CPU_TARGET_X_DISTANCE_THRESHOLD = 100;
            this.timer = (20 * 25);
            this.thrustPower = (30 * 3);
            this.thrusting = false;
            this.firing = false;
            this.cpuControls = new ControlBits();
            this.prevCpuControls = new ControlBits();
            this.cpuFireTimer = 0;
            this.cpuTarget = null;
            this.cpuTargetTimer = this.CPU_TARGET_RATE;
            this.cpuPreviousPosition = new Point();
            this.cpuStuckPositionFrames = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.finished = false;
                this.character = this.self;
                this.self.camFocus(15);
                this.self.resetMovement();
                this.deathBounds = SSF2API.getStage().getDeathBounds();
                this.self.addEventListener(SSF2Event.CHAR_SELF_DESTRUCT, this.removeSelfPlatform);
            };
        }

        internal function frame4():*
        {
            this.self.createTimer(12, 1, this.finalStartJump);
            this.self.createTimer(15, 1, this.finalStartFly);
            this.self.playVoiceSound(1);
        }

        internal function frame16():*
        {
            this.self.createTimer(1, 0, this.foxRise);
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("rise");
        }

        internal function frame20():*
        {
            this.setupBar();
            this.self.playAttackSound(3);
            this.self.updateAttackStats({
                "air_ease":this.MAX_FALL_SPEED,
                "allowControl":true
            });
            this.self.updateCharacterStats({"gravity":this.GRAVITY});
            this.self.setYSpeed(this.MAX_FALL_SPEED);
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.cleanup, {"persistent":true});
            if (this.self.isFacingRight())
            {
                this.self.createSelfPlatform(-70, -80, 265, 20, false);
            }
            else
            {
                this.self.createSelfPlatform(70, -80, -265, 20, false);
            };
            this.self.createTimer(1, 0, this.landmasterControls);
            this.self.createTimer(1, 0, this.startTimer);
            this.self.resetCPUControls();
            this.self.createTimer(1, 0, this.landmasterControlsCPU);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landmasterGrounded);
        }

        internal function frame21():*
        {
            this.firing = false;
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame50():*
        {
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame58():*
        {
            this.self.stancePlayFrame("landmaster_jump");
        }

        internal function frame59():*
        {
            this.self.destroyTimer(this.landmasterControls);
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame69():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame70():*
        {
            this.self.createTimer(1, 0, this.landmasterControls);
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame71():*
        {
            this.self.playAttackSound(9);
        }

        internal function frame80():*
        {
            this.self.fireProjectile("landmasterLaser", 0, -30);
        }

        internal function frame95():*
        {
            this.self.createTimer(1, 0, this.landmasterControls);
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame96():*
        {
            this.self.playAttackSound(7);
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame114():*
        {
            this.self.removeSelfPlatform();
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame116():*
        {
            if (this.self.isFacingRight())
            {
                this.self.faceLeft();
                this.self.createSelfPlatform(70, -80, -265, 20, false);
            }
            else
            {
                this.self.faceRight();
                this.self.createSelfPlatform(-70, -80, 265, 20, false);
            };
            this.self.updateAttackStats({"allowControl":true});
            this.self.createTimer(1, 0, this.landmasterControls);
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame117():*
        {
            this.self.removeSelfPlatform();
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame125():*
        {
            this.self.playAttackSound(8);
            this.self.updateAttackBoxStats(1, {
                "direction":75,
                "damage":22
            });
            this.self.refreshAttackID();
        }

        internal function frame148():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":50,
                "damage":15
            });
        }

        internal function frame151():*
        {
            if (this.self.isFacingRight())
            {
                this.self.createSelfPlatform(-70, -80, 265, 20, false);
            }
            else
            {
                this.self.createSelfPlatform(70, -80, -265, 20, false);
            };
            this.self.updateAttackStats({"allowControl":true});
            this.self.createTimer(1, 0, this.landmasterControls);
            this.self.stancePlayFrame("landmaster_idle");
        }

        internal function frame152():*
        {
            this.self.updateAttackStats({
                "air_ease":0,
                "allowControl":false,
                "resetMovement":true
            });
            this.self.attachEffect("landmaster_wireframe_mc", {
                "scaleX":1.15,
                "scaleY":1.15,
                "x":this.self.flipX(13.35),
                "y":-72.25
            });
            this.self.removeSelfPlatform();
            this.self.playAttackSound(10);
            this.clearBar();
        }

        internal function frame163():*
        {
            this.self.setYSpeed(-25);
            this.self.setXSpeed(6, false);
        }

        internal function frame169():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame170():*
        {
            this.self.endAttack();
        }


    }
}

