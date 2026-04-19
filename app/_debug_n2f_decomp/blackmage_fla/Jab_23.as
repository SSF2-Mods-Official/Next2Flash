package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Jab_23 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var controls:Object;
        public var used:Boolean;
        public var time:Number;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public function Jab_23() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(5, frame_6);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(12, frame_13);
            addFrameScript(18, frame_19);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var controls:Object;
            var used:Boolean;
            var time:Number;
            var pressed1:Boolean;
            var pressed2:Boolean;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.controls = this.self.getControls();
                            this.used = this.self.getGlobalVariable("jab");
                            this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                            if (this.used && (this.time <= 15))
                            {
                                this.self.stancePlayFrame("hit2");
                            };
                        };
                        this.pressed1 = false;
                        this.pressed2 = false;
        }
        internal function frame_2():* {
            this.pressed1 = false;
                        this.self.createTimer(1, 8, this.checkControls);
        }
        internal function frame_3():* {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_jab1", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
                        this.self.setGlobalVariable("jab", true);
                        this.self.playAttackSound(1);
        }
        internal function frame_4():* {
            this.self.attachEffect("global_dust_blast", {
                            "x":this.self.flipX(30),
                            "y":-15,
                            "parentLock":true
                        });
        }
        internal function frame_6():* {
            this.self.createTimer(1, 4, this.checkForGoToJab2);
        }
        internal function frame_10():* {
            this.self.endAttack();
        }
        internal function frame_11():* {
            this.self.updateAttackBoxStats(1, {
                            "power":45,
                            "direction":25,
                            "damage":5,
                            "hitLag":-1
                        });
                        this.self.refreshAttackID();
                        this.self.setGlobalVariable("jab", false);
                        this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
                        this.self.destroyTimer(this.checkControls);
                        this.self.destroyTimer(this.checkForGoToJab2);
                        this.self.playAttackSound(2);
        }
        internal function frame_12():* {
            this.self.attachEffect("global_dust_light");
                        this.self.addEffectToList(this.self.attachEffect("trail_bmage_jab2", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
        }
        internal function frame_13():* {
            this.self.attachEffect("global_dust_blast", {
                            "x":this.self.flipX(35),
                            "y":-20,
                            "parentLock":true
                        });
        }
        internal function frame_19():* {
            this.self.endAttack();
        }
    }
}
