package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Grab_106 extends MovieClip {
        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public var curSpeed:*;
        public var xDecay:*;
        public var xDecayPivot:*;
        public var isMovingRight:*;
        public var rand:int;
        public var _local_1:* = __activation__;
        public function Grab_106() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
            addFrameScript(20, frame_21);
            addFrameScript(21, frame_22);
            addFrameScript(24, frame_25);
            addFrameScript(36, frame_37);
            addFrameScript(37, frame_38);
            addFrameScript(38, frame_39);
            addFrameScript(39, frame_40);
            addFrameScript(40, frame_41);
            addFrameScript(42, frame_43);
            addFrameScript(49, frame_50);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var grabBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var touchBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            var curSpeed:*;
            var xDecay:*;
            var xDecayPivot:*;
            var isMovingRight:*;
            var rand:int;
            var _local_1:* = __activation__;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.xframe = "grab";
                        if (this.self && SSF2API.isReady())
                        {
                            this.self.setXSpeed((this.self.getXSpeed() * 0.6));
                        };
        }
        internal function frame_3():* {
            SSF2API.playSound("grab_swing3");
        }
        internal function frame_4():* {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }
        internal function frame_16():* {
            this.self.endAttack();
        }
        internal function frame_17():* {
            var _local_1:* = __activation__;
                        this.xframe = "grab";
                        this.curSpeed = this.self.getCharacterStat("max_xSpeed");
                        this.xDecay = 0.6;
                        this.xDecayPivot = 0.9;
                        this.isMovingRight = (this.self.getXSpeed() > 0);
                        this.self.createTimer(1, -1, this.xSpeedDecay);
                        this.self.addEventListener(SSF2Event.CHAR_GRAB, function (_arg_1:*=null):*
                        {
                            self.destroyTimer(xSpeedDecay);
                        });
        }
        internal function frame_21():* {
            SSF2API.playSound("grab_swing5");
        }
        internal function frame_22():* {
            this.self.attachEffect("global_dust_heavy", {
                            "x":this.self.flipX(-7),
                            "y":3,
                            "scaleX":-0.5,
                            "scaleY":-0.5
                        });
        }
        internal function frame_25():* {
            this.self.destroyTimer(this.xSpeedDecay);
        }
        internal function frame_37():* {
            this.self.endAttack();
        }
        internal function frame_38():* {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                            "x":this.self.flipX(23),
                            "y":-15,
                            "scaleX":-0.4,
                            "scaleY":-0.4
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_39():* {
            stop();
                        this.xframe = "grab";
                        this.rand = 0;
                        if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
                        {
                            this.rand = (10 * SSF2API.random());
                            if (this.rand >= 6)
                            {
                                this.self.stancePlayFrame("attack");
                            };
                        };
        }
        internal function frame_40():* {
            this.self.stancePlayFrame("grabbed2");
        }
        internal function frame_41():* {
            this.xframe = "attack";
                        this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
        }
        internal function frame_43():* {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_pummel", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-5)});
                        this.self.clearEffectsOnStateChange();
                        this.self.refreshAttackID();
        }
        internal function frame_50():* {
            this.self.stancePlayFrame("grabbed2");
        }
    }
}
