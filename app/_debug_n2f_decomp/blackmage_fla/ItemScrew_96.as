package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemScrew_96 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var speed:*;
        public var updateStats:*;
        public function ItemScrew_96() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(2, frame_3);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(14, frame_15);
            addFrameScript(18, frame_19);
            addFrameScript(50, frame_51);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hand:MovieClip;
            var hitBox:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var speed:*;
            var updateStats:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.speed = -23;
                        this.updateStats = true;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                        };
        }
        internal function frame_2():* {
            this.self.setXSpeed((this.self.getXSpeed() / 2));
                        this.self.playSound("screw1");
        }
        internal function frame_3():* {
            this.self.createTimer(1, 10, this.moveUp);
                        this.self.setYSpeed(-23);
                        this.self.playSound("screw2");
        }
        internal function frame_7():* {
            this.self.playSound("screw3");
        }
        internal function frame_9():* {
            this.updateStats = false;
                        this.self.updateAttackBoxStats(1, {
                            "power":30,
                            "kbConstant":100,
                            "damage":2,
                            "hitStun":2,
                            "selfHitStun":1
                        });
                        this.self.updateAttackBoxStats(2, {
                            "power":0,
                            "kbConstant":100,
                            "damage":2,
                            "hitStun":2,
                            "selfHitStun":1
                        });
                        this.self.updateAttackStats({"refreshRate":1});
        }
        internal function frame_11():* {
            this.self.playSound("screw4");
                        this.self.setIASA(true);
        }
        internal function frame_12():* {
            this.self.updateAttackBoxStats(1, {
                            "power":80,
                            "kbConstant":100,
                            "damage":2,
                            "hitStun":5,
                            "selfHitStun":5
                        });
                        this.self.updateAttackBoxStats(2, {
                            "power":80,
                            "kbConstant":100,
                            "damage":2,
                            "hitStun":5,
                            "selfHitStun":5
                        });
                        this.self.updateAttackStats({"refreshRate":90});
                        this.self.refreshAttackID();
        }
        internal function frame_15():* {
            this.self.playSound("screw5");
                        this.self.updateAttackStats({"air_ease":(4 + (this.self.getCharacterStat("max_ySpeed") * 0.4))});
        }
        internal function frame_19():* {
            this.self.playSound("screw6");
        }
        internal function frame_51():* {
            gotoAndStop("fallLoop");
        }
    }
}
