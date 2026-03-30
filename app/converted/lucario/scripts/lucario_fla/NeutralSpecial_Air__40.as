package lucario_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class NeutralSpecial_Air__40 extends MovieClip
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

        public function NeutralSpecial_Air__40()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 8, this.frame9, 11, this.frame12, 14, this.frame15, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 23, this.frame24, 24, this.frame25, 40, this.frame41);
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
                this.self.destroyTimer(this.chargeUp);
                this.self.destroyTimer(this.checkSpeckill);
                SSF2API.stopSound(this.voice);
                this.stopHoldSound();
                this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
                if (this.proj)
                {
                    this.proj.destroy();
                };
                this.self.endAttack();
            };
        }

        public function updateAnimation(_arg_1:*=null):void
        {
            var _local_2:* = this.scaleHelper();
            if (this.localCharge < 12)
            {
                if (this.chargeState != 0)
                {
                    this.latestPoint = new Point(-8.5, -27.5);
                    this.self.stancePlayFrame("loop1");
                    this.chargeState = 0;
                };
            }
            else if (this.localCharge < 24)
            {
                if (this.chargeState != 1)
                {
                    this.latestPoint = new Point(-9.5, -30);
                    this.self.stancePlayFrame("loop2");
                    this.chargeState = 1;
                };
            }
            else if (this.localCharge < 35)
            {
                if (this.chargeState != 2)
                {
                    this.latestPoint = new Point(-10.5, -31);
                    this.self.stancePlayFrame("loop3");
                    this.chargeState = 2;
                };
            }
            else if (this.localCharge < 45)
            {
                if (this.chargeState != 3)
                {
                    this.latestPoint = new Point(-11.5, -31);
                    this.self.stancePlayFrame("loop4");
                    this.chargeState = 3;
                };
            }
            else if (this.chargeState != 4)
            {
                this.latestPoint = new Point(-12.5, -36);
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

        public function toGround(_arg_1:*=null):void
        {
            this.self.destroyTimer(this.chargeUp);
            this.self.destroyTimer(this.checkSpeckill);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.setGlobalVariable("LucarioNSpecCharge", this.localCharge);
            this.self.setGlobalVariable("LucarioNSpecFrame", currentFrame);
            this.self.setGlobalVariable("LucarioNSpecProj", this.proj);
            this.self.setGlobalVariable("LucarioNSpecBPress", this.pressB);
            this.self.setGlobalVariable("LucarioNSpecSPress", this.pressS);
            this.self.setGlobalVariable("LucarioNSpecSFX", [this.voice, this.holdStart, this.holdLoop1, this.holdLoop2]);
            this.self.setGlobalVariable("LucarioNSpecSFXIndex", this.holdIndex);
            this.self.setGlobalVariable("LucarioNSpecSFXFrame", this.sfxFrame);
            this.self.forceAttack("b", null, true);
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
            this.latestPoint = new Point(-8.5, -27.5);
            this.pressB = false;
            this.pressS = false;
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
                        this.voice = this.self.playVoiceSound(1);
                    };
                    this.self.createTimer(1, -1, this.checkPressed);
                };
                this.self.updateAuraPaws();
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            };
        }

        internal function frame6():*
        {
            this.self.destroyTimer(this.checkPressed);
            this.proj = this.self.fireProjectile("aurasphere");
            if ((this.localCharge >= 45) || this.pressB)
            {
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
                if (this.proj)
                {
                    this.proj.destroy();
                };
                this.self.endAttack();
            }
            else
            {
                if (this.proj)
                {
                    this.self.swapDepths(this.proj);
                };
                this.self.createTimer(1, -1, this.doSoundStuff);
                this.self.createTimer(1, -1, this.chargeUp);
            };
            this.self.createTimer(4, -1, this.effects);
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
            this.latestPoint = new Point(-12.5, -36);
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            this.latestPoint = new Point(-12.5, -33.5);
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("loopFull");
        }

        internal function frame22():*
        {
            this.setProjCoords(new Point(-14, -30.9));
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setScale(this.self.flipX(this.scaleHelper()), this.scaleHelper());
            };
            this.self.updateAuraPaws();
            this.self.destroyTimer(this.effects);
        }

        internal function frame24():*
        {
            this.setProjCoords(new Point(-9.3, -25.6));
            if (this.proj)
            {
                this.proj.stancePlayFrame("shootHandler");
            };
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.setProjCoords(new Point(35.7, -24));
            this.stopHoldSound();
            if (this.localCharge < 23)
            {
                this.fireSound("1");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(2);
                };
            }
            else if (this.localCharge < 45)
            {
                this.fireSound("2");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(3);
                };
            }
            else
            {
                this.fireSound("3");
                if (!this.self.getMetalStatus())
                {
                    this.self.playVoiceSound(4);
                };
            };
            this.self.updateAuraPaws();
        }

        internal function frame41():*
        {
            this.self.endAttack();
        }


    }
}

