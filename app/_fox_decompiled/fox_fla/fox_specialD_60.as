package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_specialD_60 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var reverseBox:MovieClip;
        public var self:FoxExt;
        public var level:int;
        public var effect:*;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:*;
        public var curFrame:*;
        public var doIt:Boolean;
        public var chance:*;

        public function fox_specialD_60()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 9, this.frame10, 10, this.frame11, 13, this.frame14, 14, this.frame15, 23, this.frame24);
        }

        public function checkRelease():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if ((this.curCharge >= this.maxCharge) && !(this.controls.BUTTON1))
            {
                this.self.destroyTimer(this.checkRelease);
                this.self.setGlobalVariable("FoxDSpecCharge", this.maxCharge);
                this.self.stancePlayFrame("release");
            };
        }

        public function toAir(_arg_1:*):void
        {
            this.self.destroyTimer(this.checkRelease);
            this.self.destroyTimer(this.checkSpeckill);
            this.self.removeEventListener(SSF2Event.GROUND_LEAVE, this.toAir);
            this.self.setGlobalVariable("FoxDSpecCharge", this.curCharge);
            this.self.setGlobalVariable("FoxDSpecFrame", currentFrame);
            this.self.setGlobalVariable("FoxDSpecDoIt", this.doIt);
            this.self.forceAttack("b_down_air", null, true);
        }

        public function toReflect(_arg_1:*=null):void
        {
            this.self.stancePlayFrame("reflect");
            this.self.playSound("reflect_sfx");
            SSF2API.attachEffect("reflect_effect", {
                "x":_arg_1.data.opponent.getX(),
                "y":_arg_1.data.opponent.getY()
            });
        }

        public function toHitShield(_arg_1:*=null):void
        {
            this.self.importCPUControls([128, 1]);
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("FoxDSpecCharge", 0);
                this.self.setGlobalVariable("FoxDSpecFrame", 0);
                this.self.setGlobalVariable("FoxDSpecDoIt", false);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.level = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.maxCharge = this.self.getAttackStat("chargetime_max");
                this.curCharge = this.self.getGlobalVariable("FoxDSpecCharge");
                this.curFrame = this.self.getGlobalVariable("FoxDSpecFrame");
                this.doIt = this.self.getGlobalVariable("FoxDSpecDoIt");
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.toAir);
                this.self.addEventListener(SSF2Event.REVERSE_HIT, this.toReflect);
                if (this.self.isCPU())
                {
                    this.level = this.self.getCPULevel();
                    this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toHitShield);
                };
                if (this.curFrame == null)
                {
                    this.curFrame = 0;
                };
                if (this.curFrame > 1)
                {
                    if (!this.doIt)
                    {
                        this.self.createTimer(1, -1, this.checkRelease);
                    };
                    if (this.curCharge == null)
                    {
                        this.curCharge = 0;
                    };
                    this.self.stancePlayFrame(this.curFrame);
                }
                else
                {
                    if (this.curFrame == currentFrame)
                    {
                        this.self.updateAttackBoxStats(1, {
                            "damage":0,
                            "power":0,
                            "kbConstant":0,
                            "hasEffect":false,
                            "effectSound":null
                        });
                    }
                    else
                    {
                        this.effect = this.self.attachEffect("fox_shineStart", {
                            "scaleX":1.155,
                            "scaleY":1.155,
                            "parentLock":true,
                            "syncHitStun":true
                        });
                        this.self.attachEffect("fox_shineEffect");
                        this.self.playAttackSound(1);
                    };
                };
            };
        }

        internal function frame2():*
        {
            this.chance = 0;
            if (this.self.isCPU())
            {
                this.chance = SSF2API.random();
                if ((this.level >= 7) && (this.chance <= (0.4 + (0.2 * (this.level - 7)))))
                {
                    if (!this.self.isFacingRight())
                    {
                        this.self.importCPUControls([0, 1, 640, 1]);
                    }
                    else
                    {
                        this.self.importCPUControls([0, 1, 384, 1]);
                    };
                };
            };
            this.self.createTimer(1, -1, this.checkRelease);
            if (this.effect)
            {
                this.self.addEffectToList(this.effect);
                this.self.clearEffectsOnStateChange(false);
            };
        }

        internal function frame4():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(2);
            }
            else
            {
                this.curFrame = 0;
            };
            this.self.removeAllEffects();
            this.self.addEffectToList(this.self.attachEffect("fox_shineLoop", {
                "scaleX":1.155,
                "scaleY":1.155,
                "parentLock":true,
                "syncHitStun":true
            }));
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame11():*
        {
            this.self.removeAllEffects();
            this.self.addEffectToList(this.self.attachEffect("fox_shineReflect", {
                "scaleX":1.155,
                "scaleY":1.155,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.attachEffect("fox_shineEffect", {
                "parentLock":true,
                "syncHitStun":true
            });
            SSF2API.shakeCamera(2);
        }

        internal function frame14():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame15():*
        {
            this.doIt = true;
            this.self.removeAllEffects();
            this.self.addEffectToList(this.self.attachEffect("fox_shineFinish", {
                "scaleX":1.155,
                "scaleY":1.155,
                "parentLock":true,
                "syncHitStun":true
            }));
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

