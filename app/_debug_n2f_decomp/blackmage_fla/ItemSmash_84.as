package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemSmash_84 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public function ItemSmash_84() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(44, frame_45);
            addFrameScript(45, frame_46);
            addFrameScript(47, frame_48);
            addFrameScript(49, frame_50);
            addFrameScript(65, frame_66);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
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
        internal function frame_48():* {
            this.self.getItem().activateItem();
                        this.self.playAttackSound(1);
                        this.self.attachEffect("global_dust_heavy", {
                            "x":this.self.flipX(-7),
                            "y":3,
                            "scaleX":-0.75,
                            "scaleY":-0.75
                        });
        }
        internal function frame_50():* {
            this.self.getItem().deactivateItem();
                        this.self.updateAttackStats({"chargetime_max":0});
        }
        internal function frame_66():* {
            this.self.endAttack();
        }
    }
}
