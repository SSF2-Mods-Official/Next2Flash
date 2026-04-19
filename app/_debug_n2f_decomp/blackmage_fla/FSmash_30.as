package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class FSmash_30 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public var projectile:*;
        public function FSmash_30() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(43, frame_44);
            addFrameScript(44, frame_45);
            addFrameScript(48, frame_49);
            addFrameScript(51, frame_52);
            addFrameScript(58, frame_59);
            addFrameScript(74, frame_75);
            addFrameScript(75, frame_76);
            addFrameScript(86, frame_87);
            addFrameScript(88, frame_89);
            addFrameScript(99, frame_100);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var attackBox3:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            var projectile:*;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.xframe = null;
        }
        internal function frame_4():* {
            this.xframe = "charging";
                        this.self.createTimer(4, -1, this.effects);
        }
        internal function frame_44():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_45():* {
            this.xframe = "attack";
                        this.self.destroyTimer(this.effects);
        }
        internal function frame_49():* {
            this.self.playSound("bmbolt");
                        this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_52():* {
            this.self.attachEffect("global_dust_heavy");
                        SSF2API.getCamera().shake(6);
        }
        internal function frame_59():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":10,
                            "kbConstant":75,
                            "effect_id":"effect_elechit_light",
                            "effectSound":"brawl_zap_m"
                        });
                        this.self.updateAttackBoxStats(2, {
                            "damage":10,
                            "kbConstant":75,
                            "effect_id":"effect_elechit_light",
                            "effectSound":"brawl_zap_m"
                        });
                        this.self.updateAttackBoxStats(3, {
                            "damage":10,
                            "kbConstant":75,
                            "effect_id":"effect_elechit_light",
                            "effectSound":"brawl_zap_m"
                        });
        }
        internal function frame_75():* {
            this.self.endAttack();
        }
        internal function frame_76():* {
            this.xframe = "attack2";
                        this.self.playSound("bm_whoosh");
                        this.self.destroyTimer(this.effects);
        }
        internal function frame_87():* {
            this.self.attachEffect("global_dust_swirl");
                        this.self.attachEffect("global_sparkle", {
                            "x":this.self.flipX(15),
                            "y":-30
                        });
        }
        internal function frame_89():* {
            this.projectile = this.self.fireProjectile("fsmashfull");
        }
        internal function frame_100():* {
            this.self.endAttack();
        }
    }
}
