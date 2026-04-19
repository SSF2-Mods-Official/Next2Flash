package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class SSpecial_46 extends MovieClip {
        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var continuePlaying:Boolean;
        public var ground:Boolean;
        public function SSpecial_46() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(5, frame_6);
            addFrameScript(7, frame_8);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(20, frame_21);
            addFrameScript(25, frame_26);
            addFrameScript(28, frame_29);
            addFrameScript(34, frame_35);
            addFrameScript(35, frame_36);
            addFrameScript(36, frame_37);
            addFrameScript(37, frame_38);
            addFrameScript(39, frame_40);
            addFrameScript(40, frame_41);
            addFrameScript(41, frame_42);
            addFrameScript(43, frame_44);
            addFrameScript(44, frame_45);
            addFrameScript(45, frame_46);
            addFrameScript(49, frame_50);
            addFrameScript(51, frame_52);
            addFrameScript(52, frame_53);
            addFrameScript(54, frame_55);
            addFrameScript(55, frame_56);
            addFrameScript(57, frame_58);
            addFrameScript(58, frame_59);
            addFrameScript(61, frame_62);
            addFrameScript(62, frame_63);
            addFrameScript(65, frame_66);
            addFrameScript(66, frame_67);
            addFrameScript(69, frame_70);
            addFrameScript(70, frame_71);
            addFrameScript(73, frame_74);
            addFrameScript(74, frame_75);
            addFrameScript(75, frame_76);
            addFrameScript(81, frame_82);
            addFrameScript(87, frame_88);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var grabBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var touchBox:MovieClip;
            var self:BlackMageExt;
            var continuePlaying:Boolean;
            var ground:Boolean;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.self.createTimer(1, 0, this.checkGrabbed);
                            this.continuePlaying = false;
                            this.ground = this.self.isOnGround();
                            this.self.playSound("haste1");
                            this.self.setYSpeed(0);
                            this.self.attachEffect("global_sparkle", {
                                "x":this.self.flipX(15),
                                "y":-30
                            });
                        };
        }
        internal function frame_6():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-10),
                            "y":-4
                        });
        }
        internal function frame_8():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(100),
                            "y":-20
                        });
                        this.self.setXSpeed(0);
        }
        internal function frame_9():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(3),
                            "y":-8
                        });
                        this.self.attachEffect("global_dust_heavy");
        }
        internal function frame_11():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(14),
                            "y":-13
                        });
        }
        internal function frame_21():* {
            this.self.destroyTimer(this.checkGrabbed);
        }
        internal function frame_26():* {
            this.self.attachEffect("global_dust_cloud");
                        this.self.updateAttackStats({"air_ease":-0.3});
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_s");
                        };
        }
        internal function frame_29():* {
            if (!this.self.isOnGround())
                        {
                            this.self.setAttackEnabled(false, "b_forward");
                            this.self.setAttackEnabled(false, "b_forward_air");
                            this.self.endAttack();
                        };
        }
        internal function frame_35():* {
            this.self.setAttackEnabled(false, "b_forward");
                        this.self.setAttackEnabled(false, "b_forward_air");
                        this.self.endAttack();
        }
        internal function frame_36():* {
            this.self.playSound("haste2");
                        this.self.attachEffect("global_sparkle", {
                            "x":this.self.flipX(15),
                            "y":-30
                        });
                        this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-90),
                            "y":-45
                        });
        }
        internal function frame_37():* {
            if (!this.self.isOnGround())
                        {
                            this.self.setXSpeed(0);
                        };
                        this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-60),
                            "y":-45
                        });
        }
        internal function frame_38():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-30),
                            "y":-45
                        });
        }
        internal function frame_40():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-90),
                            "y":-45
                        });
        }
        internal function frame_41():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-60),
                            "y":-45
                        });
        }
        internal function frame_42():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-30),
                            "y":-45
                        });
        }
        internal function frame_44():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-90),
                            "y":-45
                        });
        }
        internal function frame_45():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-60),
                            "y":-45
                        });
        }
        internal function frame_46():* {
            this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-30),
                            "y":-45
                        });
        }
        internal function frame_50():* {
            this.self.playSound("bm_sw_m");
        }
        internal function frame_52():* {
            this.self.refreshAttackID();
        }
        internal function frame_53():* {
            this.self.playSound("bm_sw_s");
        }
        internal function frame_55():* {
            this.self.refreshAttackID();
        }
        internal function frame_56():* {
            this.self.playSound("bm_sw_m");
        }
        internal function frame_58():* {
            this.self.refreshAttackID();
        }
        internal function frame_59():* {
            this.self.playSound("bm_sw_s");
        }
        internal function frame_62():* {
            this.self.updateAttackBoxStats(1, {"damage":1});
                        this.self.refreshAttackID();
        }
        internal function frame_63():* {
            this.self.playSound("bm_sw_m");
        }
        internal function frame_66():* {
            this.self.refreshAttackID();
        }
        internal function frame_67():* {
            this.self.playSound("bm_sw_m");
        }
        internal function frame_70():* {
            this.self.refreshAttackID();
        }
        internal function frame_71():* {
            this.self.playSound("bm_sw_m");
        }
        internal function frame_74():* {
            this.self.updateAttackBoxStats(1, {
                            "selfHitStun":2,
                            "damage":7,
                            "hasEffect":true
                        });
                        this.self.updateAttackStats({
                            "canFallOff":true,
                            "xSpeedDecayAir":-0.15
                        });
                        this.self.refreshAttackID();
        }
        internal function frame_75():* {
            this.self.playSound("bm_sw_l");
                        this.self.attachEffect("global_dust_heavy");
        }
        internal function frame_76():* {
            this.self.releaseOpponent();
                        this.self.setXSpeed(17.5, false);
        }
        internal function frame_82():* {
            this.self.setXSpeed(0, false);
        }
        internal function frame_88():* {
            this.self.endAttack();
        }
    }
}
