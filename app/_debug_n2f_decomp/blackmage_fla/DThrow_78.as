package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DThrow_78 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public function DThrow_78() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(4, frame_5);
            addFrameScript(7, frame_8);
            addFrameScript(8, frame_9);
            addFrameScript(11, frame_12);
            addFrameScript(25, frame_26);
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
        internal function frame_2():* {
            this.self.forceGrabbedHurtFrame("faint");
        }
        internal function frame_5():* {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dthrow_bubble", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_8():* {
            this.self.playAttackSound(1);
        }
        internal function frame_9():* {
            this.xframe = "attack";
        }
        internal function frame_12():* {
            this.self.forceGrabbedHurtFrame("downed");
        }
        internal function frame_26():* {
            this.self.endAttack();
        }
    }
}
