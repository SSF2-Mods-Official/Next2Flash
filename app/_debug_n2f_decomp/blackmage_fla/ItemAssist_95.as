package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemAssist_95 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemAssist_95() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(7, frame_8);
            addFrameScript(30, frame_31);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_8():* {
            this.self.getItem().activateItem();
        }
        internal function frame_31():* {
            this.self.endAttack();
        }
    }
}
