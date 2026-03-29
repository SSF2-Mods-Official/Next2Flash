package
{
    public dynamic class Main extends SSF2Asset
    {

        public var stageMC:stage_battlefield;

        public function Main()
        {
            super();
            addFrameScript(1, this.frame2);
            register("id", "battlefield");
            register("guid", "ad6f95ac-4566-40eb-9ad3-e75702242cfd");
            register("resources", {
                "movieclips":["battlefield_bg", "stage_battlefield"],
                "sounds":[]
            });
            register("music", [{"id":"bgm_battlefield"}, {"id":"bgm_multimansmash"}, {"id":"bgm_cruelsmash"}]);
            register("stage", Battlefield);
            register("camera", {
                "x_start":590,
                "y_start":350,
                "backgrounds":[{"linkage_id":"battlefield_bg"}]
            });
        }

        internal function frame2():*
        {
            stop();
        }


    }
}

