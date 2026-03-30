package lucario_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class NeutralSpecial_Ground__39 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
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
        public var curFrame:int;
        public var saund:*;

        public function NeutralSpecial_Ground__39()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 8, this.frame9, 11, this.frame12, 14, this.frame15, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 24, this.frame25, 25, this.frame26, 26, this.frame27, 27, this.frame28, 28, this.frame29, 29, this.frame30, 30, this.frame31, 31, this.frame32, 32, this.frame33, 33, this.frame34, 34, this.frame35, 35, this.frame36, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 41, this.frame42, 42, this.frame43, 43, this.frame44, 45, this.frame46, 46, this.frame47, 62, this.frame63);
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
                    this.latestPoint = new Point(-10.3, -24.6);
                    this.self.stancePlayFrame("loop1");
                    this.chargeState = 0;
                };
            }
            else if (this.localCharge < 24)
            {
                if (this.chargeState != 1)
                {
                    this.latestPoint = new Point(-12.5, -25.9);
                    this.self.stancePlayFrame("loop2");
                    this.chargeState = 1;
                };
            }
            else if (this.localCharge < 35)
            {
                if (this.chargeState != 2)
                {
                    this.latestPoint = new Point(-13.8, -27.1);
                    this.self.stancePlayFrame("loop3");
                    this.chargeState = 2;
                };
            }
            else if (this.localCharge < 45)
            {
                if (this.chargeState != 3)
                {
                    this.latestPoint = new Point(-16.3, -27.1);
                    this.self.stancePlayFrame("loop4");
                    this.chargeState = 3;
                };
            }
            else if (this.chargeState != 4)
            {
                this.latestPoint = new Point(-16.9, -29.1);
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
            if ((this.self.getCurrentAnimation() != "grab") && (this.self.getCurrentAnimation() != "b"))
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
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.localCharge = 0;
            this.maxCharge = 45;
            this.chargeState = 0;
            this.latestPoint = new Point(-10.3, -24.6);
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
            this.curFrame = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.localCharge = this.self.getGlobalVariable("LucarioNSpecCharge");
                this.self.setGlobalVariable("LucarioNSpecCharge", 0);
                if (this.localCharge >= this.maxCharge)
                {
                    this.localCharge = this.maxCharge;
                };
                this.curFrame = this.self.getGlobalVariable("LucarioNSpecFrame");
                this.self.setGlobalVariable("LucarioNSpecFrame", 0);
                if (this.curFrame > 0)
                {
                    this.proj = this.self.getGlobalVariable("LucarioNSpecProj");
                    this.self.setGlobalVariable("LucarioNSpecProj", null);
                    this.pressB = this.self.getGlobalVariable("LucarioNSpecBPress");
                    this.self.setGlobalVariable("LucarioNSpecBPress", false);
                    this.pressS = this.self.getGlobalVariable("LucarioNSpecSPress");
                    this.self.setGlobalVariable("LucarioNSpecSPress", false);
                    this.saund = this.self.getGlobalVariable("LucarioNSpecSFX");
                    if (this.saund != null)
                    {
                        this.voice = this.saund[0];
                        this.holdStart = this.saund[1];
                        this.holdLoop1 = this.saund[2];
                        this.holdLoop2 = this.saund[3];
                    };
                    this.self.setGlobalVariable("LucarioNSpecSFX", null);
                    this.holdIndex = this.self.getGlobalVariable("LucarioNSpecSFXIndex");
                    this.self.setGlobalVariable("LucarioNSpecSFXIndex", -1);
                    this.sfxFrame = this.self.getGlobalVariable("LucarioNSpecSFXFrame");
                    this.self.setGlobalVariable("LucarioNSpecSFXFrame", 0);
                };
                this.self.updateAuraPaws();
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                if (this.curFrame > 1)
                {
                    if (this.curFrame < 6)
                    {
                        this.self.createTimer(1, -1, this.checkPressed);
                    }
                    else if (this.curFrame < 22)
                    {
                        this.self.createTimer(1, -1, this.doSoundStuff);
                        this.self.createTimer(1, -1, this.chargeUp);
                        this.self.createTimer(4, -1, this.effects);
                    }
                    else
                    {
                        this.curFrame += 22;
                    };
                    this.self.stancePlayFrame(this.curFrame);
                }
                else if (this.localCharge < this.maxCharge)
                {
                    if (this.voice != null)
                    {
                        SSF2API.stopSound(this.voice);
                    };
                    if (!this.self.getMetalStatus())
                    {
                        this.voice = this.self.playVoiceSound(1);
                    };
                    this.self.createTimer(1, -1, this.checkPressed);
                };
            };
        }

        internal function frame6():*
        {
            if (this.curFrame != currentFrame)
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
            this.latestPoint = new Point(-16.9, -29.1);
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            this.latestPoint = new Point(-16.9, -28.4);
        }

        internal function frame21():*
        {
            this.latestPoint = new Point(-16.9, -29.1);
        }

        internal function frame22():*
        {
            this.latestPoint = new Point(-16.9, -28.4);
        }

        internal function frame23():*
        {
            this.latestPoint = new Point(-16.9, -29.1);
        }

        internal function frame24():*
        {
            this.latestPoint = new Point(-16.9, -28.4);
        }

        internal function frame25():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame26():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame27():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame28():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame29():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame30():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame31():*
        {
            this.latestPoint = new Point(-15, -28.4);
        }

        internal function frame32():*
        {
            this.latestPoint = new Point(-15, -27);
        }

        internal function frame33():*
        {
            this.latestPoint = new Point(-15, -28.4);
        }

        internal function frame34():*
        {
            this.latestPoint = new Point(-15, -27);
        }

        internal function frame35():*
        {
            this.latestPoint = new Point(-15, -28.4);
        }

        internal function frame36():*
        {
            this.latestPoint = new Point(-15, -27);
        }

        internal function frame37():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame38():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame39():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame40():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame41():*
        {
            this.latestPoint = new Point(-16.3, -27.1);
        }

        internal function frame42():*
        {
            this.latestPoint = new Point(-16.3, -26.4);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("loopFull");
        }

        internal function frame44():*
        {
            if (this.curFrame != currentFrame)
            {
                if (this.proj && !(this.proj.isDisposed()))
                {
                    this.proj.setScale(this.self.flipX(this.scaleHelper()), this.scaleHelper());
                };
                this.self.updateAuraPaws();
                this.self.destroyTimer(this.effects);
            };
            this.setProjCoords(new Point(-14, -30.9));
        }

        internal function frame46():*
        {
            if (this.curFrame != currentFrame)
            {
                if (this.proj)
                {
                    this.proj.stancePlayFrame("shootHandler");
                };
                this.self.updateAuraPaws();
            };
            this.setProjCoords(new Point(-9.3, -25.6));
        }

        internal function frame47():*
        {
            if (this.curFrame != currentFrame)
            {
                this.stopHoldSound();
                if (this.localCharge < 23)
                {
                    this.fireSound("1");
                    if (!this.self.getMetalStatus())
                    {
                        this.self.playVoiceSound(2);
                    };
                    this.self.attachEffect("global_dust_light");
                }
                else if (this.localCharge < 45)
                {
                    this.fireSound("2");
                    if (!this.self.getMetalStatus())
                    {
                        this.self.playVoiceSound(3);
                    };
                    this.self.attachEffect("global_dust_heavy", {
                        "scaleX":0.5,
                        "scaleY":0.5
                    });
                }
                else
                {
                    this.fireSound("3");
                    if (!this.self.getMetalStatus())
                    {
                        this.self.playVoiceSound(4);
                    };
                    this.self.attachEffect("global_dust_heavy");
                };
                this.self.updateAuraPaws();
            };
            this.setProjCoords(new Point(35.7, -24));
        }

        internal function frame63():*
        {
            this.self.endAttack();
        }


    }
}

