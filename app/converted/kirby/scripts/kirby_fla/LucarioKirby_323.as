package kirby_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class LucarioKirby_323 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var localCharge:Number;
        public var maxCharge:int;
        public var chargeState:int;
        public var proj:*;
        public var latestPoint:Point;
        public var controls:Object;
        public var pressB:Boolean;
        public var pressS:Boolean;
        public var pressG:Boolean;
        public var pressL:Boolean;
        public var pressR:Boolean;
        public var baseScale:Number;
        public var baseAuraScale:Number;
        public var chargeScale:Number;
        public var chargeAuraScale:Number;
        public var voice:*;
        public var holdLengths:Array;
        public var holdStart:*;
        public var holdLoop1:*;
        public var holdLoop2:*;
        public var holdIndex:*;
        public var sfxFrame:*;

        public function LucarioKirby_323()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 8, this.frame9, 11, this.frame12, 14, this.frame15, 17, this.frame18, 18, this.frame19, 20, this.frame21, 22, this.frame23, 24, this.frame25, 26, this.frame27, 28, this.frame29, 30, this.frame31, 31, this.frame32, 33, this.frame34, 34, this.frame35, 50, this.frame51);
        }

        public function checkPressed():void
        {
            this.controls = this.self.getControls(true);
            if (this.controls.BUTTON1)
            {
                this.pressB = true;
            };
            if (this.controls.SHIELD)
            {
                this.pressS = true;
            };
            if (this.controls.GRAB)
            {
                this.pressG = true;
            };
            if (this.controls.LEFT)
            {
                this.pressL = true;
            };
            if (this.controls.RIGHT)
            {
                this.pressR = true;
            };
        }

        public function chargeUp():void
        {
            this.checkPressed();
            if (this.localCharge < this.maxCharge)
            {
                this.localCharge++;
            };
            this.updateAnimation();
            if (this.pressB)
            {
                this.self.destroyTimer(this.chargeUp);
                this.self.destroyTimer(this.checkSpeckill);
                SSF2API.stopSound(this.voice);
                this.self.setGlobalVariable("LucarioNSpecCharge", 0);
                if (this.proj)
                {
                    this.self.swapDepths(this.proj);
                };
                this.self.stancePlayFrame("fire");
            }
            else if (this.pressS)
            {
                this.cancelAttack();
                this.self.endAttack();
            }
            else if (this.self.isOnGround())
            {
                if (this.pressG)
                {
                    this.cancelAttack();
                    this.self.addEventListener(SSF2Event.CHAR_GRAB, this.grabbed, {"persistent":true});
                    this.self.addEventListener(SSF2Event.STATE_CHANGE, this.clearGrabEvent, {"persistent":true});
                    this.self.forceAttack("grab");
                }
                else if (this.pressL)
                {
                    this.cancelAttack();
                    this.self.faceLeft();
                    this.self.toDodgeRoll();
                }
                else if (this.pressR)
                {
                    this.cancelAttack();
                    this.self.faceRight();
                    this.self.toDodgeRoll();
                };
            }
            else
            {
                this.pressG = false;
                this.pressL = false;
                this.pressR = false;
            };
        }

        public function cancelAttack():void
        {
            this.self.destroyTimer(this.chargeUp);
            this.self.destroyTimer(this.checkSpeckill);
            SSF2API.stopSound(this.voice);
            this.stopHoldSound();
            this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
            if (this.proj)
            {
                this.proj.destroy();
            };
        }

        public function updateAnimation(_arg_1:*=null):void
        {
            var _local_2:* = this.scaleHelper();
            if (this.localCharge < 12)
            {
                if (this.chargeState != 0)
                {
                    this.latestPoint = new Point(-17.5, -7.5);
                    this.self.stancePlayFrame("loop1");
                    this.chargeState = 0;
                };
            }
            else if (this.localCharge < 24)
            {
                if (this.chargeState != 1)
                {
                    this.latestPoint = new Point(-19, -9.5);
                    this.self.stancePlayFrame("loop2");
                    this.chargeState = 1;
                };
            }
            else if (this.localCharge < 35)
            {
                if (this.chargeState != 2)
                {
                    this.latestPoint = new Point(-21, -12);
                    this.self.stancePlayFrame("loop3");
                    this.chargeState = 2;
                };
            }
            else if (this.localCharge < 45)
            {
                if (this.chargeState != 3)
                {
                    this.latestPoint = new Point(-21.5, -18);
                    this.self.stancePlayFrame("loop4");
                    this.chargeState = 3;
                };
            }
            else if (this.chargeState != 4)
            {
                this.latestPoint = new Point(-18.5, -19.5);
                this.self.attachEffect("effect_aura_charge", {
                    "x":this.self.flipX(this.latestPoint.x),
                    "y":this.latestPoint.y,
                    "scaleX":_local_2,
                    "scaleY":_local_2,
                    "behind":true
                });
                this.self.stancePlayFrame("loopFull");
                this.chargeState = 4;
            };
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale(this.self.flipX(_local_2), _local_2);
                if (this.latestPoint)
                {
                    this.setProjCoords(this.latestPoint);
                };
            };
        }

        public function scaleHelper():Number
        {
            return ((this.baseScale + (this.baseAuraScale * this.self.auraPercentage)) + ((this.localCharge / 45) * this.chargeScale)) + (((this.localCharge / 45) * this.chargeAuraScale) * this.self.auraPercentage);
        }

        public function setProjCoords(_arg_1:Point):void
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setX(((this.self.getX() + (this.self.flipX(_arg_1.x) * this.self.getScale().x)) + this.self.getXSpeed()));
                this.proj.setY(((this.self.getY() + (_arg_1.y * this.self.getScale().y)) + this.self.getYSpeed()));
                this.latestPoint = _arg_1;
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("LucarioNSpecCharge", 0);
                this.stopSFX();
            };
        }

        public function getAuraLevel():Number
        {
            if (this.self.auraPercentage < 0.33)
            {
                return 0;
            }
            else
            if (this.self.auraPercentage < 0.67)
            {
                return 1;
            }
            else
            {
            return 2;
            };
        }

        public function getAuraString():String
        {
            if (this.self.auraPercentage < 0.33)
            {
                return "S";
            }
            else
            if (this.self.auraPercentage < 0.67)
            {
                return "M";
            }
            else
            {
            return "L";
            };
        }

        public function doSoundStuff():void
        {
            this.sfxFrame++;
            if (this.holdIndex == -1)
            {
                this.holdStart = this.self.playSound(("lucario_nspec_holdStart" + this.getAuraString()));
                this.holdIndex = 0;
                this.sfxFrame = 0;
            }
            else if (this.holdIndex == 0)
            {
                if (this.sfxFrame >= this.holdLengths[this.getAuraLevel()])
                {
                    this.holdLoop1 = this.self.playSound(("lucario_nspec_holdLoop" + this.getAuraString()));
                    this.holdIndex = 1;
                    this.sfxFrame = 0;
                };
            }
            else if (this.sfxFrame >= 34)
            {
                if (this.holdIndex == 1)
                {
                    this.holdLoop2 = this.self.playSound(("lucario_nspec_holdLoop" + this.getAuraString()));
                    this.holdIndex = 2;
                }
                else
                {
                    this.holdLoop1 = this.self.playSound(("lucario_nspec_holdLoop" + this.getAuraString()));
                    this.holdIndex = 1;
                };
                this.sfxFrame = 0;
            };
        }

        public function fireSound(_arg_1:String):void
        {
            if (this.self.auraPercentage < 0.33)
            {
                this.self.playSound(("lucario_nspec_a" + _arg_1));
            }
            else if (this.self.auraPercentage < 0.67)
            {
                this.self.playSound(("lucario_nspec_b" + _arg_1));
            }
            else
            {
                this.self.playSound(("lucario_nspec_c" + _arg_1));
            };
        }

        public function stopHoldSound():void
        {
            this.self.destroyTimer(this.doSoundStuff);
            if (this.holdStart != null)
            {
                SSF2API.stopSound(this.holdStart);
            };
            if (this.holdLoop1 != null)
            {
                SSF2API.stopSound(this.holdLoop1);
            };
            if (this.holdLoop2 != null)
            {
                SSF2API.stopSound(this.holdLoop2);
            };
        }

        public function stopSFX():void
        {
            if (this.voice != null)
            {
                SSF2API.stopSound(this.voice);
            };
            this.stopHoldSound();
        }

        public function grabbed(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.clearGrabEvent);
            if (this.self.getCurrentAnimation() == "grab")
            {
                SSF2API.playSound("grab");
                this.self.toGrabbing();
            };
            this.self.removeEventListener(SSF2Event.CHAR_GRAB, this.grabbed);
        }

        public function clearGrabEvent(_arg_1:*=null):*
        {
            if ((this.self.getCurrentAnimation() != "grab") && (this.self.getCurrentAnimation() != "kirby_lucario"))
            {
                this.self.removeEventListener(SSF2Event.CHAR_GRAB, this.grabbed);
                this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.clearGrabEvent);
            };
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.localCharge = 0;
            this.maxCharge = 45;
            this.chargeState = 0;
            this.latestPoint = new Point(-17.5, -7.5);
            this.pressB = false;
            this.pressS = false;
            this.pressG = false;
            this.pressL = false;
            this.pressR = false;
            this.baseScale = 0.45;
            this.baseAuraScale = 0.8;
            this.chargeScale = 1;
            this.chargeAuraScale = 1.2;
            this.holdLengths = [49, 50, 22];
            this.holdIndex = -1;
            this.sfxFrame = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.localCharge = this.self.getGlobalVariable("LucarioNSpecCharge");
                this.self.setGlobalVariable("LucarioNSpecCharge", 0);
                if (this.localCharge >= this.maxCharge)
                {
                    this.localCharge = this.maxCharge;
                }
                else
                {
                    if (!this.self.getMetalStatus())
                    {
                        this.voice = this.self.playSound("lucario_kirby_nspec0", true);
                    };
                    this.self.createTimer(1, -1, this.checkPressed);
                };
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
            };
        }

        internal function frame6():*
        {
            this.self.destroyTimer(this.checkPressed);
            if ((this.localCharge >= 45) || this.pressB)
            {
                this.proj = this.self.fireProjectile("aurasphere");
                if (this.voice != null)
                {
                    SSF2API.stopSound(this.voice);
                };
                this.self.setGlobalVariable("LucarioNSpecCharge", 0);
                this.self.stancePlayFrame("fire");
            }
            else if (this.pressS)
            {
                if (this.voice != null)
                {
                    SSF2API.stopSound(this.voice);
                };
                this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
                this.self.endAttack();
            }
            else if (this.self.isOnGround() && this.pressG)
            {
                if (this.voice != null)
                {
                    SSF2API.stopSound(this.voice);
                };
                this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
                this.self.addEventListener(SSF2Event.CHAR_GRAB, this.grabbed, {"persistent":true});
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.clearGrabEvent, {"persistent":true});
                this.self.forceAttack("grab");
            }
            else if (this.self.isOnGround() && this.pressL)
            {
                if (this.voice != null)
                {
                    SSF2API.stopSound(this.voice);
                };
                this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
                this.self.faceLeft();
                this.self.toDodgeRoll();
            }
            else if (this.self.isOnGround() && this.pressR)
            {
                if (this.voice != null)
                {
                    SSF2API.stopSound(this.voice);
                };
                this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
                this.self.faceRight();
                this.self.toDodgeRoll();
            }
            else
            {
                this.pressG = false;
                this.pressL = false;
                this.pressR = false;
                this.proj = this.self.fireProjectile("aurasphere");
                if (this.proj)
                {
                    this.self.swapDepths(this.proj);
                };
                this.self.createTimer(1, -1, this.doSoundStuff);
                this.self.createTimer(1, -1, this.chargeUp);
                this.self.createTimer(4, -1, this.effects);
            };
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("loop1");
        }

        internal function frame12():*
        {
            this.self.stancePlayFrame("loop2");
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("loop3");
        }

        internal function frame18():*
        {
            this.self.stancePlayFrame("loop4");
        }

        internal function frame19():*
        {
            this.setProjCoords(new Point(-18.5, -19.5));
        }

        internal function frame21():*
        {
            this.setProjCoords(new Point(-19.5, -18));
        }

        internal function frame23():*
        {
            this.setProjCoords(new Point(-19.5, -15.5));
        }

        internal function frame25():*
        {
            this.setProjCoords(new Point(-19.5, -15.5));
        }

        internal function frame27():*
        {
            this.setProjCoords(new Point(-20.5, -16.5));
        }

        internal function frame29():*
        {
            this.setProjCoords(new Point(-20, -18));
        }

        internal function frame31():*
        {
            this.self.stancePlayFrame("loopFull");
        }

        internal function frame32():*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale(this.self.flipX(this.scaleHelper()), this.scaleHelper());
            };
            this.setProjCoords(new Point(-24, -19));
            this.self.destroyTimer(this.effects);
        }

        internal function frame34():*
        {
            if (this.proj)
            {
                this.proj.stancePlayFrame("shootHandler");
            };
            this.setProjCoords(new Point(-5, -18));
        }

        internal function frame35():*
        {
            this.stopHoldSound();
            if (this.localCharge < 23)
            {
                this.fireSound("1");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(1);
                };
                if (this.self.isOnGround())
                {
                    this.self.attachEffect("global_dust_light");
                };
            }
            else if (this.localCharge < 45)
            {
                this.fireSound("2");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(1);
                };
                if (this.self.isOnGround())
                {
                    this.self.attachEffect("global_dust_heavy", {
                        "scaleX":0.5,
                        "scaleY":0.5
                    });
                };
            }
            else
            {
                this.fireSound("3");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(2);
                };
                if (this.self.isOnGround())
                {
                    this.self.attachEffect("global_dust_heavy");
                };
            };
            this.setProjCoords(new Point(14.5, -16));
        }

        internal function frame51():*
        {
            this.self.endAttack();
        }


    }
}

