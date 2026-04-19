package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Hurts_107 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public function Hurts_107() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(8, frame_9);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(18, frame_19);
            addFrameScript(19, frame_20);
            addFrameScript(20, frame_21);
            addFrameScript(28, frame_29);
            addFrameScript(29, frame_30);
            addFrameScript(30, frame_31);
            addFrameScript(38, frame_39);
            addFrameScript(39, frame_40);
            addFrameScript(40, frame_41);
            addFrameScript(49, frame_50);
            addFrameScript(58, frame_59);
            addFrameScript(59, frame_60);
            addFrameScript(60, frame_61);
            addFrameScript(66, frame_67);
            addFrameScript(68, frame_69);
            addFrameScript(69, frame_70);
            addFrameScript(70, frame_71);
            addFrameScript(78, frame_79);
            addFrameScript(79, frame_80);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.xframe = "hurt1";
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            this.self.setGlobalVariable("jab", false);
                        };
        }
        internal function frame_9():* {
            stop();
        }
        internal function frame_10():* {
            this.self.stancePlayFrame("done1");
        }
        internal function frame_11():* {
            this.xframe = "hurt2";
                        this.self.setGlobalVariable("jab", false);
        }
        internal function frame_19():* {
            stop();
        }
        internal function frame_20():* {
            this.self.stancePlayFrame("done2");
        }
        internal function frame_21():* {
            this.xframe = "hurt3";
                        this.self.setGlobalVariable("jab", false);
        }
        internal function frame_29():* {
            stop();
        }
        internal function frame_30():* {
            this.self.stancePlayFrame("done3");
        }
        internal function frame_31():* {
            this.xframe = "downed";
        }
        internal function frame_39():* {
            this.xframe = "downed";
                        stop();
        }
        internal function frame_40():* {
            this.self.stancePlayFrame("downed");
        }
        internal function frame_41():* {
            this.xframe = "shock";
        }
        internal function frame_50():* {
            this.self.stancePlayFrame("shock");
        }
        internal function frame_59():* {
            this.xframe = "ball";
                        stop();
        }
        internal function frame_60():* {
            this.self.stancePlayFrame("ball");
        }
        internal function frame_61():* {
            this.xframe = "faint";
        }
        internal function frame_67():* {
            this.self.attachEffect("effect_land");
                        SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
        internal function frame_69():* {
            this.xframe = "faintDone";
                        stop();
        }
        internal function frame_70():* {
            this.self.stancePlayFrame("faintDone");
        }
        internal function frame_71():* {
            this.xframe = "spin";
        }
        internal function frame_79():* {
            this.xframe = "spin";
                        stop();
        }
        internal function frame_80():* {
            this.self.stancePlayFrame("spin");
        }
    }
}
