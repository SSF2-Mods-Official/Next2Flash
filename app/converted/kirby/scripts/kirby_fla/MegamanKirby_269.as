package kirby_fla
{
    import flash.display.MovieClip;
    import flash.geom.ColorTransform;
    import flash.events.Event;

    public dynamic class MegamanKirby_269 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var STND:int;
        public var MOVE:int;
        public var JUMP:int;
        public var FALL:int;
        public var LAND:int;
        public var SHOT:int;
        public var ENDG:int;
        public var state:int;
        public var jumpForce:*;
        public var shortHop:*;
        public var groundSpeed:*;
        public var airSpeed:*;
        public var groundAccel:*;
        public var airAccel:*;
        public var curSpeed:*;
        public var chargeLim1:int;
        public var chargeLim2:int;
        public var chargeLim3:int;
        public var shots:int;
        public var shotLimit:int;
        public var chargeCount:*;
        public var frameCount:int;
        public var fireFrame:int;
        public var refireFrame:int;
        public var endFrame:int;
        public var reenableFrame:int;
        public var curFrame:int;
        public var heldControls:*;
        public var pressedControls:*;
        public var heldShot:Boolean;
        public var shotReady:Boolean;
        public var hasMidairJump:Boolean;
        public var useShortHop:Boolean;
        public var chargeFlash:ColorTransform;
        public var startSFX:*;
        public var holdSFX:*;
        public var thisMC:*;
        public var fjmp_shot1:int;
        public var fjmp_shot2:int;

        public function MegamanKirby_269()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 12, this.frame13, 22, this.frame23, 24, this.frame25, 28, this.frame29, 29, this.frame30, 32, this.frame33, 34, this.frame35, 35, this.frame36, 38, this.frame39, 40, this.frame41, 42, this.frame43, 43, this.frame44, 49, this.frame50, 64, this.frame65, 65, this.frame66, 71, this.frame72, 86, this.frame87);
        }

        public function update():void
        {
            this.heldControls = this.self.getControls();
            this.pressedControls = this.self.getControls(true);
            this.checkState();
            if ((this.state == this.MOVE) || (((this.state == this.JUMP) || (this.state == this.FALL) || (this.state == this.ENDG)) && (this.heldControls.LEFT != this.heldControls.RIGHT)))
            {
                this.checkMove();
            }
            else
            {
                this.curSpeed = this.self.getXSpeed();
            };
            if (this.state != this.SHOT)
            {
                this.checkFrame();
            };
        }

        public function checkState():void
        {
            switch (this.state)
            {
                case this.STND:
                case this.LAND:
                    this.setState(this.JUMP);
                    this.setState(this.FALL);
                    this.setState(this.MOVE);
                    break;
                case this.MOVE:
                    this.setState(this.JUMP);
                    this.setState(this.FALL);
                    this.setState(this.STND);
                    break;
                case this.FALL:
                    this.setState(this.JUMP);
                    this.setState(this.LAND);
                    break;
                case this.ENDG:
                    this.setState(this.JUMP);
                    this.setState(this.MOVE);
                    break;
                case this.JUMP:
                case this.SHOT:
                case 7:
                default:
                    break;
            }
        }

        public function setState(_arg_1:int):void
        {
            if (this.state == _arg_1)
            {
                return;
            };
            this.state = _arg_1;
            switch (this.state)
            {
            case this.STND:
            this.self.updateAttackStats({"disableJump":false});
            this.self.stancePlayFrame("stand");
            break;
            case this.MOVE:
            this.self.updateAttackStats({"disableJump":false});
            this.self.stancePlayFrame("move");
            break;
            case this.JUMP:
            this.useShortHop = this.heldControls.DOWN;
            this.hasMidairJump = this.self.isOnGround();
            this.self.updateAttackStats({"disableJump":!(this.hasMidairJump)});
            this.self.stancePlayFrame("jump");
            break;
            case this.FALL:
            this.self.stancePlayFrame("fall");
            break;
            case this.LAND:
            this.self.updateAttackStats({"disableJump":false});
            this.self.stancePlayFrame("land");
            break;
            case this.SHOT:
            this.self.destroyTimer(this.update);
            this.self.updateAttackStats({"allowTurn":false});
            this.self.stancePlayFrame("shot");
            break;
            case this.ENDG:
            this.self.stancePlayFrame("end");
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.stancePlayFrame("endAir");
            break;
            case 7:
            default:
            break;
            }
        }

        public function checkMove():void
        {
            if (this.heldControls.LEFT)
            {
                this.curSpeed *= -1;
            };
            if (this.self.isOnGround())
            {
                if (this.curSpeed < 0)
                {
                    this.curSpeed = 0;
                };
                this.curSpeed += this.groundAccel;
                if (this.curSpeed > this.groundSpeed)
                {
                    this.curSpeed = this.groundSpeed;
                };
            }
            else
            {
                this.curSpeed += this.airAccel;
                if (this.curSpeed > this.airSpeed)
                {
                    this.curSpeed = this.airSpeed;
                };
            };
            this.self.setXSpeed(this.curSpeed, false);
            if (this.heldControls.LEFT)
            {
                this.curSpeed *= -1;
            };
        }

        public function checkFrame():void
        {
            if ((this.frameCount == (this.fireFrame - 1)) && !(this.shotReady) && this.heldControls.BUTTON1)
            {
                this.chargeCount++;
                this.applyCharge();
                return;
            };
            this.frameCount++;
            if (this.frameCount < this.fireFrame)
            {
                if (!(this.shotReady) && !(this.heldControls.BUTTON1))
                {
                    this.shotReady = true;
                };
            }
            else if (this.frameCount == this.fireFrame)
            {
                this.self.destroyTimer(this.busterStart);
                this.self.destroyTimer(this.busterHold);
                this.busterEnd();
                this.heldShot = false;
                this.shotReady = false;
                this.setBright(0);
                this.thisMC.transform.colorTransform = this.chargeFlash;
                if (this.chargeCount > this.chargeLim3)
                {
                    this.shots = this.shotLimit;
                    this.setState(this.SHOT);
                }
                else
                {
                    if (this.chargeCount > this.chargeLim2)
                    {
                        this.self.playAttackSound(2);
                        this.self.fireProjectile("megaman_buster3", -1, -8);
                        this.self.attachEffect("global_dust_light");
                    }
                    else if (this.chargeCount > this.chargeLim1)
                    {
                        this.self.playAttackSound(1);
                        this.self.fireProjectile("megaman_buster2", -1, -8);
                        this.self.attachEffect("global_dust_light");
                    }
                    else
                    {
                        this.self.playAttackSound(1);
                        this.self.fireProjectile("megaman_buster1", 5, -8);
                    };
                    this.chargeCount = 0;
                    this.shots++;
                    if ((this.state == this.JUMP) || (this.state == this.LAND) || (this.state == this.ENDG))
                    {
                        if (this.self.isOnGround())
                        {
                            this.setState(this.STND);
                        }
                        else
                        {
                            this.setState(this.FALL);
                        };
                    };
                };
            }
            else if (this.frameCount < this.refireFrame)
            {
            }
            else if (this.frameCount < this.reenableFrame)
            {
                if ((this.frameCount == this.endFrame) && (this.state != this.JUMP) && (this.state != this.MOVE))
                {
                    this.setState(this.ENDG);
                };
                if (this.heldControls.BUTTON1)
                {
                    this.heldShot = true;
                }
                else if (this.heldShot && !(this.shotReady))
                {
                    this.shotReady = true;
                };
                if (this.heldShot)
                {
                    if (this.heldControls.UP)
                    {
                        if (this.self.isOnGround())
                        {
                            this.self.forceAttack("b_up", true);
                        }
                        else
                        {
                            this.self.forceAttack("b_up_air", true);
                        };
                    }
                    else if (this.shots < this.shotLimit)
                    {
                        this.frameCount = 0;
                        this.self.createTimer(7, 1, this.busterStart);
                        this.self.createTimer(40, -1, this.busterHold);
                        if (this.state == this.ENDG)
                        {
                            if (this.self.isOnGround())
                            {
                                this.setState(this.STND);
                            }
                            else
                            {
                                this.setState(this.FALL);
                            };
                        };
                    };
                };
            }
            else if (this.heldControls.BUTTON1 || this.heldShot)
            {
                this.shots = 0;
                this.frameCount = 0;
                this.self.createTimer(7, 1, this.busterStart);
                this.self.createTimer(40, -1, this.busterHold);
                if (this.state == this.ENDG)
                {
                    if (this.self.isOnGround())
                    {
                        this.setState(this.STND);
                    }
                    else
                    {
                        this.setState(this.FALL);
                    };
                };
            }
            else
            {
                this.self.endAttack();
            };
        }

        public function toGround(_arg_1:Event=null):void
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            if (this.self.getMetalStatus())
            {
                SSF2API.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
            if (this.state == this.SHOT)
            {
            }
            else if (this.state == this.ENDG)
            {
                this.self.stancePlayFrame("end");
            };
        }

        public function applyCharge():void
        {
            this.setBright(0);
            if (this.chargeCount < this.chargeLim1)
            {
                if ((this.chargeCount % 2) != 0)
                {
                    this.setBright(20);
                    this.chargeFlash.redOffset += 30;
                };
            }
            else if (this.chargeCount < this.chargeLim2)
            {
                if ((this.chargeCount % 2) != 0)
                {
                    this.setBright(45);
                };
                this.chargeFlash.redOffset += 30;
            }
            else if (this.chargeCount < this.chargeLim3)
            {
                this.setBright(45);
                if ((this.chargeCount % 2) != 0)
                {
                    this.chargeFlash.redOffset += 100;
                };
            }
            else
            {
                if ((this.chargeCount % 2) != 0)
                {
                    this.setBright(50);
                }
                else
                {
                    this.setBright(-50);
                };
                this.chargeFlash.redOffset -= 10;
            };
            this.thisMC.transform.colorTransform = this.chargeFlash;
        }

        public function setBright(_arg_1:int):void
        {
            this.chargeFlash.redOffset = _arg_1;
            this.chargeFlash.blueOffset = _arg_1;
            this.chargeFlash.greenOffset = _arg_1;
        }

        public function busterStart():void
        {
            this.startSFX = SSF2API.playSound("megaman_buster_holdStart");
        }

        public function busterHold():void
        {
            this.holdSFX = SSF2API.playSound("megaman_buster_holdLoop");
        }

        public function busterEnd(_arg_1:Event=null):void
        {
            if (this.startSFX != null)
            {
                SSF2API.stopSound(this.startSFX);
                this.startSFX = null;
            };
            if (this.holdSFX != null)
            {
                SSF2API.stopSound(this.holdSFX);
                this.holdSFX = null;
            };
        }

        public function toGroundShot(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGroundShot);
            this.self.updateAttackStats({"disableJump":false});
            if (this.self.getMetalStatus())
            {
                SSF2API.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
            this.curFrame = (currentFrame - (this.fjmp_shot2 - this.fjmp_shot1));
            this.self.stancePlayFrame(this.curFrame);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.STND = 0;
            this.MOVE = 1;
            this.JUMP = 2;
            this.FALL = 3;
            this.LAND = 4;
            this.SHOT = 5;
            this.ENDG = 6;
            this.state = this.STND;
            this.jumpForce = -12;
            this.shortHop = -8.7;
            this.groundSpeed = 5.8;
            this.airSpeed = 9;
            this.groundAccel = 0.9;
            this.airAccel = 1.5;
            this.curSpeed = 0;
            this.chargeLim1 = 15;
            this.chargeLim2 = 25;
            this.chargeLim3 = 45;
            this.shots = 0;
            this.shotLimit = 3;
            this.chargeCount = 0;
            this.frameCount = 0;
            this.fireFrame = 4;
            this.refireFrame = 7;
            this.endFrame = 11;
            this.reenableFrame = 19;
            this.curFrame = 0;
            this.heldShot = true;
            this.shotReady = false;
            this.hasMidairJump = true;
            this.useShortHop = false;
            this.chargeFlash = new ColorTransform();
            this.startSFX = null;
            this.holdSFX = null;
            if (SSF2API.isReady() && this.self)
            {
                this.thisMC = this.self.getStanceMC();
                if (this.self.getMidairJumpCount() > 0)
                {
                    this.hasMidairJump = false;
                };
                this.self.createTimer(1, -1, this.update);
                this.self.createTimer(7, 1, this.busterStart);
                this.self.createTimer(40, -1, this.busterHold);
                this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.busterEnd);
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.busterEnd);
                if (!this.self.isOnGround())
                {
                    this.state = this.FALL;
                    this.self.stancePlayFrame("startAir");
                };
            };
        }

        internal function frame4():*
        {
            this.self.stancePlayFrame("stand");
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step01");
            };
        }

        internal function frame23():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step02");
            };
        }

        internal function frame25():*
        {
            this.self.stancePlayFrame("move");
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("fall");
        }

        internal function frame30():*
        {
            if (!this.hasMidairJump)
            {
                this.self.setYSpeed(this.jumpForce);
                this.self.playSound("ssf2_snd_sfx_kirby_jump01");
            };
        }

        internal function frame33():*
        {
            if (this.hasMidairJump)
            {
                if (this.useShortHop)
                {
                    this.self.setYSpeed(this.shortHop);
                }
                else
                {
                    this.self.setYSpeed(this.jumpForce);
                };
                this.self.attachEffect("global_dust_cloud");
                this.self.playSound("ssf2_snd_sfx_kirby_jump01");
            };
        }

        internal function frame35():*
        {
            this.setState(this.FALL);
        }

        internal function frame36():*
        {
            if (this.self.getMetalStatus())
            {
                SSF2API.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame39():*
        {
            this.setState(this.STND);
        }

        internal function frame41():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("endAir");
        }

        internal function frame44():*
        {
            this.fjmp_shot1 = currentFrame;
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"disableJump":false});
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGroundShot);
                this.self.stancePlayFrame("shotAir");
            };
        }

        internal function frame50():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(3);
                this.self.fireProjectile("megaman_buster_full", 15, -10);
                this.self.attachEffect("global_dust_heavy");
                this.self.setXSpeed(-7, false);
            };
        }

        internal function frame65():*
        {
            this.self.endAttack();
        }

        internal function frame66():*
        {
            this.fjmp_shot2 = currentFrame;
        }

        internal function frame72():*
        {
            this.self.playAttackSound(3);
            this.self.fireProjectile("megaman_buster_full", 15, -10);
            this.self.attachEffect("global_dust_heavy");
            this.self.setXSpeed(-7, false);
        }

        internal function frame87():*
        {
            this.self.endAttack();
        }


    }
}

