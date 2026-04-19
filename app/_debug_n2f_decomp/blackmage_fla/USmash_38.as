package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class USmash_38 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public function USmash_38() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(44, frame_45);
            addFrameScript(45, frame_46);
            addFrameScript(46, frame_47);
            addFrameScript(47, frame_48);
            addFrameScript(61, frame_62);
            addFrameScript(62, frame_63);
            addFrameScript(63, frame_64);
            addFrameScript(81, frame_82);
            addFrameScript(86, frame_87);
            addFrameScript(88, frame_89);
            addFrameScript(90, frame_91);
            addFrameScript(94, frame_95);
            addFrameScript(128, frame_129);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.xframe = null;
        }
        internal function frame_5():* {
            this.xframe = "charging";
                        this.self.createTimer(4, -1, this.effects);
        }
        internal function frame_45():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_46():* {
            this.xframe = "attack";
                        this.self.destroyTimer(this.effects);
        }
        internal function frame_47():* {
            this.self.playAttackSound(2);
                        this.self.attachEffect("global_dust_cloud");
                        this.self.attachEffect("global_dust_swirl");
                        this.self.addEffectToList(this.self.attachEffect("blackmage_usmash_uncharged", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_48():* {
            this.self.playAttackSound(3);
        }
        internal function frame_62():* {
            this.self.attachEffect("effect_land");
                        SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landHeavy");
                        };
        }
        internal function frame_63():* {
            this.self.endAttack();
        }
        internal function frame_64():* {
            this.xframe = "attack2";
                        this.self.destroyTimer(this.effects);
                        this.self.updateAttackStats({"refreshRate":1});
                        this.self.updateAttackBoxStats(2, {
                            "direction":20,
                            "power":45,
                            "damage":1,
                            "hitStun":1,
                            "selfHitStun":0,
                            "priority":-1,
                            "reversableAngle":false,
                            "effectSound":"brawl_fire_m"
                        });
                        this.self.updateAttackBoxStats(1, {
                            "direction":160,
                            "power":45,
                            "damage":1,
                            "hitStun":1,
                            "selfHitStun":0,
                            "priority":-1,
                            "reversableAngle":false,
                            "effectSound":"brawl_fire_m"
                        });
                        this.self.playAttackSound(1);
        }
        internal function frame_82():* {
            this.self.playAttackSound(2);
                        this.self.updateAttackStats({"refreshRate":200});
                        this.self.updateAttackBoxStats(1, {
                            "direction":90,
                            "power":10,
                            "hitStun":17,
                            "sdiDistance":0
                        });
                        this.self.refreshAttackID();
        }
        internal function frame_87():* {
            this.self.attachEffect("global_sparkle", {"y":-20});
        }
        internal function frame_89():* {
            this.self.updateAttackBoxStats(1, {
                            "power":105,
                            "kbConstant":50,
                            "hitStun":1,
                            "damage":15,
                            "sdiDistance":1
                        });
                        this.self.refreshAttackID();
                        SSF2API.getCamera().shake(7);
        }
        internal function frame_91():* {
            this.self.updateAttackBoxStats(1, {"power":100});
        }
        internal function frame_95():* {
            this.self.updateAttackBoxStats(1, {"damage":10});
        }
        internal function frame_129():* {
            this.self.endAttack();
        }
    }
}
