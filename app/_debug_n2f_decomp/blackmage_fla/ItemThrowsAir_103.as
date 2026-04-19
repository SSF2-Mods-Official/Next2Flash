package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemThrowsAir_103 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemThrowsAir_103() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(3, frame_4);
            addFrameScript(11, frame_12);
            addFrameScript(12, frame_13);
            addFrameScript(13, frame_14);
            addFrameScript(15, frame_16);
            addFrameScript(23, frame_24);
            addFrameScript(24, frame_25);
            addFrameScript(25, frame_26);
            addFrameScript(27, frame_28);
            addFrameScript(35, frame_36);
            addFrameScript(36, frame_37);
            addFrameScript(37, frame_38);
            addFrameScript(39, frame_40);
            addFrameScript(47, frame_48);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                        };
        }
        internal function frame_2():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_4():* {
            this.self.tossItem(158);
        }
        internal function frame_12():* {
            this.self.endAttack();
        }
        internal function frame_13():* {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }
        internal function frame_14():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_16():* {
            this.self.tossItem(270);
        }
        internal function frame_24():* {
            this.self.endAttack();
        }
        internal function frame_25():* {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }
        internal function frame_26():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_28():* {
            this.self.tossItem(90);
        }
        internal function frame_36():* {
            this.self.endAttack();
        }
        internal function frame_37():* {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }
        internal function frame_38():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_40():* {
            this.self.tossItem(12);
        }
        internal function frame_48():* {
            this.self.endAttack();
        }
    }
}
