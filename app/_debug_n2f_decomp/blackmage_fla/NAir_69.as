package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class NAir_69 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var _local_2:* = this.self.getYSpeed();
        public var _local_3:* = this.self.getXSpeed();
        public var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
        public var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 4);
        public function NAir_69() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(12, frame_13);
            addFrameScript(14, frame_15);
            addFrameScript(16, frame_17);
            addFrameScript(22, frame_23);
            addFrameScript(23, frame_24);
            addFrameScript(24, frame_25);
            addFrameScript(31, frame_32);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var attackBox3:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var _local_2:* = this.self.getYSpeed();
            var _local_3:* = this.self.getXSpeed();
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 4);
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.self.setLandingLag(false);
                        };
        }
        internal function frame_3():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(20),
                            "y":-25
                        });
                        this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-20),
                            "y":-35
                        });
                        this.self.createTimer(1, -1, this.setAngle);
        }
        internal function frame_4():* {
            this.self.playAttackSound(1);
                        this.self.setLandingLag(true);
        }
        internal function frame_5():* {
            this.self.refreshAttackID();
        }
        internal function frame_7():* {
            this.self.refreshAttackID();
        }
        internal function frame_9():* {
            this.self.refreshAttackID();
        }
        internal function frame_11():* {
            this.self.refreshAttackID();
        }
        internal function frame_13():* {
            this.self.refreshAttackID();
        }
        internal function frame_15():* {
            this.self.refreshAttackID();
        }
        internal function frame_17():* {
            this.self.destroyTimer(this.setAngle);
                        this.self.updateAttackBoxStats(1, {
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.updateAttackBoxStats(2, {
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.updateAttackBoxStats(3, {
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.refreshAttackID();
                        this.self.setLandingLag(false);
        }
        internal function frame_23():* {
            this.self.endAttack();
        }
        internal function frame_24():* {
            this.self.destroyTimer(this.setAngle);
                        this.self.updateAttackBoxStats(1, {
                            "damage":2,
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.updateAttackBoxStats(2, {
                            "damage":2,
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.updateAttackBoxStats(3, {
                            "damage":2,
                            "power":63,
                            "weightKB":0,
                            "kbConstant":80,
                            "direction":45,
                            "reversableAngle":true,
                            "hitLag":-1,
                            "hitStun":-1,
                            "selfHitStun":-1
                        });
                        this.self.refreshAttackID();
        }
        internal function frame_25():* {
            SSF2API.getCamera().shake(3);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landHeavy");
                        };
        }
        internal function frame_32():* {
            this.self.endAttack();
        }
    }
}
