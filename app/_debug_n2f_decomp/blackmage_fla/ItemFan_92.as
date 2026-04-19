package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemFan_92 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemFan_92() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(5, frame_6);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_3():* {
            this.self.getItem().activateItem();
                        this.self.playAttackSound(1);
                        this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }
        internal function frame_4():* {
            this.self.getItem().deactivateItem();
        }
        internal function frame_6():* {
            this.self.endAttack();
        }
    }
}
