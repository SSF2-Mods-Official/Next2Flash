package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class BThrow_79 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public function BThrow_79() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(4, frame_5);
            addFrameScript(5, frame_6);
            addFrameScript(6, frame_7);
            addFrameScript(7, frame_8);
            addFrameScript(8, frame_9);
            addFrameScript(23, frame_24);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var touchBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.xframe = null;
        }
        internal function frame_3():* {
            SSF2API.getCamera().shake(2);
                        this.self.playAttackSound(1);
        }
        internal function frame_5():* {
            this.xframe = "attack";
        }
        internal function frame_6():* {
            SSF2API.getCamera().shake(2);
        }
        internal function frame_7():* {
            this.self.playAttackSound(2);
        }
        internal function frame_8():* {
            SSF2API.getCamera().shake(4);
        }
        internal function frame_9():* {
            this.self.fireProjectile("bthrowrock");
        }
        internal function frame_24():* {
            this.self.endAttack();
        }
    }
}
