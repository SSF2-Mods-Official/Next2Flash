package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemDashAttack_82 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemDashAttack_82() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(5, frame_6);
            addFrameScript(7, frame_8);
            addFrameScript(23, frame_24);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_6():* {
            this.self.getItem().activateItem();
                        this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }
        internal function frame_8():* {
            this.self.getItem().deactivateItem();
        }
        internal function frame_24():* {
            this.self.endAttack();
        }
    }
}
